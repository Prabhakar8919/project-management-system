// Enhanced navigation active state management
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.main-nav a');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        
        // Remove active class from all links first
        link.classList.remove('active');
        
        // Add active class based on current path
        if (currentPath === '/') {
            document.querySelector('.main-nav a[href="/"]').classList.add('active');
        } else if (currentPath.startsWith('/projects/')) {
            // Check if it's Project Workplace related (studio, create, edit, delete)
            if (currentPath.includes('/studio') || 
                currentPath.includes('/create') || 
                currentPath.includes('/edit') || 
                currentPath.includes('/delete')) {
                document.querySelector('.main-nav a[href="/projects/studio/"]').classList.add('active');
            } 
            // Otherwise it's Project Explorer
            else if (currentPath === '/projects/' || currentPath === '/projects') {
                document.querySelector('.main-nav a[href="/projects/"]').classList.add('active');
            }
        } else if (currentPath.startsWith('/dashboard')) {
            document.querySelector('.main-nav a[href="/dashboard/"]').classList.add('active');
        }
    });
});
