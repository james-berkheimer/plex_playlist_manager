
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



// $(document).ready(function() {
//     $('a[media-library]').on('click', function(e) {
//         e.preventDefault(); // Prevent the default action of the link
//         var libraryName = $(this).attr('media-library'); // Get the library name from the attribute
//         var titles = mediaData[libraryName].map(function(item) { // Get the titles of all items for the clicked library
//             return item.title;
//         });
//         $('#media_container').text(titles.join(', ')); // Display the titles in the media_container div
//     });
// });


// $(document).ready(function() {
//     // Fetch the template file
//     var xhr = new XMLHttpRequest();
//     xhr.open('GET', '/pages/media_container', true);
//     xhr.onreadystatechange = function () {
//         console.log('Hello from xhr.onreadystatechange');
//         if (xhr.readyState === 4 && xhr.status === 200) {
//             var template = xhr.responseText;
//             console.log('Template:', template);  // Check if the template is fetched correctly

//             $('a[media-library]').on('click', function(e) {
//                 e.preventDefault(); // Prevent the default action of the link
//                 var libraryName = $(this).attr('media-library'); // Get the library name from the attribute
//                 var titles = mediaData[libraryName].map(function(item) { // Get the titles of all items for the clicked library
//                     return item.title;
//                 });
//                 console.log('titles:', titles)

//                 // Use the template to create new elements
//                 var html = '';
//                 for (var i = 0; i < titles.length; i++) {
//                     var itemHtml = template
//                         .replace('{{title}}', titles[i])
//                         .replace('{{thumb_path}}', mediaData[libraryName][i].thumb_path)
//                         .replace('{{year}}', mediaData[libraryName][i].year);
//                     html += itemHtml;
//                 }
//                 $('#media_container').html(html); // Display the titles in the media_container div
//             });
//         }
//     };
//     xhr.send();
// });