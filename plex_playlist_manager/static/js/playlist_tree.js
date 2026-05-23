/**
 * Alpine component for the playlist tree view.
 *
 * Holds selection state (a Set of playlistItemID values) and the helpers
 * the template needs to drive selectors and the action bar.
 *
 * Registered as a global function so the template can reference it via
 * x-data="playlistTree()".
 */
window.playlistTree = function () {
    return {
        selectedLetter: "ALL",
        selected: new Set(),

        toggleTrack(id) {
            if (this.selected.has(id)) {
                this.selected.delete(id);
            } else {
                this.selected.add(id);
            }
        },

        toggleGroup(idsAttr) {
            const ids = idsAttr
                .split(",")
                .filter((s) => s.length)
                .map(Number);
            const state = this.groupState(ids);
            if (state === "checked") {
                ids.forEach((id) => this.selected.delete(id));
            } else {
                ids.forEach((id) => this.selected.add(id));
            }
        },

        groupState(ids) {
            if (ids.length === 0) return "unchecked";
            let hits = 0;
            for (const id of ids) {
                if (this.selected.has(id)) hits++;
            }
            if (hits === 0) return "unchecked";
            if (hits === ids.length) return "checked";
            return "partial";
        },

        trackState(id) {
            return this.selected.has(id) ? "checked" : "unchecked";
        },

        /**
         * Issue a batch DELETE for the currently-selected playlistItemIDs.
         * On success, surgically remove the deleted rows and reconcile all
         * counts in place — no full re-render.
         *
         * @param {string|number} playlistId - The Plex playlist ratingKey.
         */
        async remove(playlistId) {
            const idsToDelete = Array.from(this.selected);
            if (idsToDelete.length === 0) return;

            const params = new URLSearchParams();
            for (const id of idsToDelete) {
                params.append("playlist_item_id", id);
            }
            const url = `/playlists/${playlistId}/items?${params.toString()}`;

            this.selected = new Set();

            try {
                const response = await fetch(url, { method: "DELETE" });
                if (!response.ok) {
                    console.error(
                        `Delete request failed: ${response.status} ${response.statusText}`,
                    );
                    return;
                }
                this.reconcile(idsToDelete);
            } catch (err) {
                console.error("Delete request error:", err);
            }
        },

        /**
         * Surgically remove deleted tracks from the DOM and reconcile every
         * count, duration, letter-strip entry, and sidebar entry to match
         * the new state of the tree.
         *
         * No server round-trip; all math is done from data-* attributes on
         * the rendered DOM. Expand state, scroll position, and any other
         * non-deleted DOM nodes are preserved.
         *
         * @param {Iterable<number|string>} deletedIds - The playlistItemID
         *     values that were successfully deleted.
         */
        reconcile(deletedIds) {
            const root = document.querySelector("[data-tree-root]");
            if (!root) return;

            const idsToRemove = new Set(
                Array.from(deletedIds).map((v) => String(v)),
            );

            // 1. Remove the deleted track <li> rows.
            const trackRows = root.querySelectorAll("[data-track-row]");
            for (const li of trackRows) {
                const id = li.getAttribute("data-playlist-item-id");
                if (id !== null && idsToRemove.has(id)) {
                    li.remove();
                }
            }

            // 2. Remove emptied album <details> nodes; otherwise update album
            //    track count.
            const albumNodes = root.querySelectorAll("[data-album-node]");
            for (const album of albumNodes) {
                const remaining = album.querySelectorAll("[data-track-row]");
                if (remaining.length === 0) {
                    album.remove();
                } else {
                    const countSpan = album.querySelector(
                        "[data-album-track-count]",
                    );
                    if (countSpan) {
                        countSpan.textContent = String(remaining.length);
                    }
                }
            }

            // 3. Remove emptied artist <details> nodes; otherwise update
            //    artist album and track counts.
            const artistNodes = root.querySelectorAll("[data-artist-node]");
            for (const artist of artistNodes) {
                const remainingAlbums =
                    artist.querySelectorAll("[data-album-node]");
                if (remainingAlbums.length === 0) {
                    artist.remove();
                    continue;
                }
                const remainingTracks =
                    artist.querySelectorAll("[data-track-row]");
                const albumCountSpan = artist.querySelector(
                    "[data-artist-album-count]",
                );
                const trackCountSpan = artist.querySelector(
                    "[data-artist-track-count]",
                );
                if (albumCountSpan) {
                    albumCountSpan.textContent = String(remainingAlbums.length);
                }
                if (trackCountSpan) {
                    trackCountSpan.textContent = String(remainingTracks.length);
                }
            }

            // 4. Recompute and update header counts and total duration.
            const survivingArtists =
                root.querySelectorAll("[data-artist-node]");
            const survivingTracks = root.querySelectorAll("[data-track-row]");
            let totalMs = 0;
            for (const li of survivingTracks) {
                const ms = parseInt(
                    li.getAttribute("data-duration-ms") || "0",
                    10,
                );
                if (!Number.isNaN(ms)) totalMs += ms;
            }

            const headerArtistCount = root.querySelector(
                "[data-header-artist-count]",
            );
            const headerTrackCount = root.querySelector(
                "[data-header-track-count]",
            );
            const headerDuration = root.querySelector(
                "[data-header-duration]",
            );
            if (headerArtistCount) {
                headerArtistCount.textContent = String(survivingArtists.length);
            }
            if (headerTrackCount) {
                headerTrackCount.textContent = String(survivingTracks.length);
            }
            if (headerDuration) {
                headerDuration.textContent = this.formatDuration(totalMs);
                headerDuration.setAttribute(
                    "data-duration-ms",
                    String(totalMs),
                );
            }

            // 5. Recompute which letters are still present.
            const presentLetters = new Set();
            for (const artist of survivingArtists) {
                const letter = artist.getAttribute("data-bucket-letter");
                if (letter) presentLetters.add(letter);
            }
            this.updateLetterStrip(presentLetters);

            // 6. Update the sidebar count for the active playlist.
            const playlistId = root.getAttribute("data-playlist-id");
            this.updateSidebarCount(playlistId, survivingTracks.length);

            // 7. If the currently-active letter filter no longer has any
            //    artists, fall back to ALL so the user isn't staring at an
            //    empty view.
            if (
                this.selectedLetter !== "ALL" &&
                !presentLetters.has(this.selectedLetter)
            ) {
                this.selectedLetter = "ALL";
            }
        },

        /**
         * Enable letter-strip buttons whose letter is in `presentLetters`,
         * disable the rest. Mirrors the server-side rendering logic that
         * sets `disabled` and toggles class names for absent letters.
         *
         * @param {Set<string>} presentLetters
         */
        updateLetterStrip(presentLetters) {
            const buttons = document.querySelectorAll("[data-letter-button]");
            const activeClasses = [
                "text-plex-text",
                "hover:bg-plex-elevated",
                "cursor-pointer",
            ];
            const inactiveClasses = [
                "text-plex-muted",
                "opacity-30",
                "cursor-not-allowed",
            ];

            for (const button of buttons) {
                const letter = button.getAttribute("data-letter-button");
                const present = presentLetters.has(letter);
                if (present) {
                    button.removeAttribute("disabled");
                    inactiveClasses.forEach((c) => button.classList.remove(c));
                    activeClasses.forEach((c) => button.classList.add(c));
                } else {
                    button.setAttribute("disabled", "");
                    activeClasses.forEach((c) => button.classList.remove(c));
                    inactiveClasses.forEach((c) => button.classList.add(c));
                }
            }
        },

        /**
         * Update the active playlist's track count in the sidebar.
         *
         * The sidebar is rendered by index.html and lives outside the
         * tree-container, so it isn't refreshed by tree swaps.
         *
         * @param {string} playlistId
         * @param {number} newCount
         */
        updateSidebarCount(playlistId, newCount) {
            const target = document.querySelector(
                `[data-sidebar-playlist-id="${playlistId}"] [data-sidebar-track-count]`,
            );
            if (target) {
                target.textContent = String(newCount);
            }
        },

        /**
         * Format a millisecond duration as H:MM:SS or M:SS, matching the
         * Jinja format_duration macro.
         *
         * @param {number} ms
         * @returns {string}
         */
        formatDuration(ms) {
            const totalSeconds = Math.floor(ms / 1000);
            const hours = Math.floor(totalSeconds / 3600);
            const minutes = Math.floor((totalSeconds % 3600) / 60);
            const seconds = totalSeconds % 60;
            const pad = (n) => String(n).padStart(2, "0");
            if (hours > 0) {
                return `${hours}:${pad(minutes)}:${pad(seconds)}`;
            }
            return `${minutes}:${pad(seconds)}`;
        },
    };
};