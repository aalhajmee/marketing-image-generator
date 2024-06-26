document.getElementById('imageForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const title = document.getElementById('title').value;
    const subtitle = document.getElementById('subtitle').value;
    const category = document.getElementById('category').value;
    const backgroundUrl = document.getElementById('background_url').value;
    const keywordsList = document.getElementById('keywords').value.split(',').map(keyword => keyword.trim());

    try {
        const response = await fetch('http://bam.alhajmee.com/generate-image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                subtitle: subtitle,
                category: category,
                background_url: backgroundUrl,
                keywords: keywordsList
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }

        const data = await response.json();
        // Handle the response data
        console.log(data);
        const imageUrl = data.image_url;
        document.getElementById('generatedImage').src = imageUrl;
        document.getElementById('generatedImageContainer').style.display = 'block';
    } catch (error) {
        console.error('There has been a problem with your fetch operation:', error.message);
        alert('Error: ' + error.message);
    }
});
