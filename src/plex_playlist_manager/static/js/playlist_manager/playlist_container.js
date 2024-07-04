console.log('Loading playlist_container.js');

// Event listener for fetching playlists
document.addEventListener('DOMContentLoaded', function() {
    var playlistItems = document.querySelectorAll('.playlist-item');
    var playlistContents = document.getElementById('playlistContent');

    playlistItems.forEach(function(playlistItem) {
        playlistItem.addEventListener('click', function() {
            // Remove the selected class from all items
            playlistItems.forEach(function(item) {
                item.classList.remove('selected');
            });

            // Add the selected class to the clicked item
            this.classList.add('selected');

            // Clear the playlistContent div
            playlistContents.innerHTML = '';

            // Get the playlist title and type
            var playlistTitle = this.textContent.trim();
            var playlistType = this.dataset.playlistType;

            // Send a request to the server with the playlist title and type
            fetch('/get_playlist_items', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'playlist_title': playlistTitle,
                    'playlist_type': playlistType
                })
            })
            .then(response => response.text())
            .then(data => {
                // document.getElementById('playlistContent').innerHTML = data;
                playlistContents.innerHTML = data;
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

// -----------------------------------------------------------------------------------

// Event listener for rotating SVG icons
document.addEventListener('DOMContentLoaded', function() {
    console.log('Event listener for rotating SVG icons');
    document.addEventListener('click', function(event) {
        if (event.target.closest('.click-area')) {
            const svgIcon = event.target.closest('.click-area').querySelector('svg');
            if (svgIcon) {
                svgIcon.style.transform = svgIcon.style.transform === 'rotate(180deg)' ? '' : 'rotate(180deg)';
            }
        }
    });
});

// -----------------------------------------------------------------------------------

// Event listener for managing checkbox interactions
document.addEventListener('DOMContentLoaded', function() {
    console.log('Event listener for managing checkbox interactions');
    const playlistContent = document.getElementById('playlistContent');

    playlistContent.addEventListener('click', function(event) {
        let target = event.target;
        let container = target.closest('.checkbox-container');

        if (container) {
            // Prevent the default checkbox toggle since we'll handle it programmatically
            event.preventDefault();

            let checkbox = container.querySelector('span[type="checkbox"]');
            if (checkbox) {
                // Toggle 'checked' class and checkbox checked state
                checkbox.checked = !checkbox.checked;
                toggleCheckboxContainerClass(checkbox, checkbox.checked);
                console.log('Checkbox changed:', checkbox.id);

                // Additional logic for toggling child checkboxes
                toggleChildCheckboxes(checkbox);
            }
        }

        // Prevent double toggling for clicks directly on the checkbox
        if (target.matches('span[type="checkbox"]')) {
            event.stopPropagation();
        }
    });

    function toggleCheckboxContainerClass(checkbox, isChecked) {
        if (isChecked) {
            checkbox.closest('.checkbox-container').classList.add('checked');
        } else {
            checkbox.closest('.checkbox-container').classList.remove('checked');
        }
    }

    function toggleChildCheckboxes(checkbox) {
        let checkboxType = checkbox.classList.contains('artist-checkbox') || checkbox.classList.contains('show-checkbox') ? 'artist' : 'album';
        let idParts = checkbox.id.split('--');
        let childCheckboxPattern = `${idParts[0]}--${(checkboxType === 'artist' || checkboxType === 'show') ? '' : idParts[1] + '--'}`;

        document.querySelectorAll('span[type="checkbox"]').forEach(function(childCheckbox) {
            if (childCheckbox.id.startsWith(childCheckboxPattern)) {
                console.log('Toggling child checkbox:', childCheckbox.id);
                childCheckbox.checked = checkbox.checked;
                toggleCheckboxContainerClass(childCheckbox, checkbox.checked);
            }
        });
    }
});