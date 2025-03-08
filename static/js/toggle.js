// Function to toggle between light and dark modes
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.toggle('dark-mode');

    // Save the current theme in localStorage
    if (currentTheme) {
        localStorage.setItem('theme', 'dark');
    } else {
        localStorage.setItem('theme', 'light');
    }
}

// Function to load the saved theme from localStorage
function loadTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.toggle('dark-mode', savedTheme === 'dark');
    }
}

// Add event listener to the theme toggle button
document.addEventListener('DOMContentLoaded', function() {
    const themeToggleButton = document.getElementById('theme-toggle');
    themeToggleButton.addEventListener('click', toggleTheme);

    // Load the saved theme when the page loads
    loadTheme();
});
