
import React, { useState } from 'react';

const MediaLibrary = ({ mediaData }) => {
    const [titles, setTitles] = useState([]);

    const handleClick = (libraryName) => {
        const libraryTitles = mediaData[libraryName].map(item => item.title);
        setTitles(libraryTitles);
    };

    return (
        <div>
            {Object.keys(mediaData).map(libraryName => (
                <a key={libraryName} onClick={() => handleClick(libraryName)}>
                    {libraryName}
                </a>
            ))}
            <div id="media_container">{titles.join(', ')}</div>
        </div>
    );
};

export default MediaLibrary;

