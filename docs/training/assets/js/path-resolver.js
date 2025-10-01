/**
 * Path Resolver for SAMA PROMIS Training Site
 * Automatically converts relative paths to absolute paths when opened in file:// mode
 */

(function() {
    'use strict';
    
    // Detect if we're in file:// mode
    const isFileProtocol = window.location.protocol === 'file:';
    
    if (!isFileProtocol) {
        // Running on a web server, no need to resolve paths
        console.log('Running on web server, path resolution not needed');
        return;
    }
    
    console.log('File protocol detected, enabling path resolution');
    
    /**
     * Calculate the base path to /docs/training/
     * Works from any depth in the directory structure
     */
    function getBasePath() {
        const currentPath = window.location.pathname;
        
        // Find the position of '/docs/training/' in the path
        const trainingIndex = currentPath.indexOf('/docs/training/');
        
        if (trainingIndex === -1) {
            console.error('Could not find /docs/training/ in path:', currentPath);
            return '';
        }
        
        // Extract the base path up to and including /docs/training/
        const basePath = currentPath.substring(0, trainingIndex + '/docs/training/'.length);
        
        // Convert to file:// URL format
        return 'file://' + basePath;
    }
    
    /**
     * Resolve a relative path to an absolute path
     * @param {string} relativePath - The relative path (e.g., '../../assets/css/main.css')
     * @returns {string} - The absolute path
     */
    function resolvePath(relativePath) {
        if (!relativePath) return relativePath;
        
        // If already absolute, return as-is
        if (relativePath.startsWith('http://') || 
            relativePath.startsWith('https://') || 
            relativePath.startsWith('file://') ||
            relativePath.startsWith('#')) {
            return relativePath;
        }
        
        const basePath = getBasePath();
        const currentPath = window.location.pathname;
        const currentDir = currentPath.substring(0, currentPath.lastIndexOf('/') + 1);
        
        // Handle different relative path formats
        if (relativePath.startsWith('../')) {
            // Go up directories
            let path = currentDir;
            let relPath = relativePath;
            
            while (relPath.startsWith('../')) {
                path = path.substring(0, path.lastIndexOf('/', path.length - 2) + 1);
                relPath = relPath.substring(3);
            }
            
            return 'file://' + path + relPath;
        } else if (relativePath.startsWith('./')) {
            // Current directory
            return 'file://' + currentDir + relativePath.substring(2);
        } else if (!relativePath.startsWith('/')) {
            // Relative to current directory
            return 'file://' + currentDir + relativePath;
        } else {
            // Absolute path from root
            return 'file://' + relativePath;
        }
    }
    
    /**
     * Fix all links and resources on the page
     */
    function fixAllPaths() {
        // Fix all <a> tags
        document.querySelectorAll('a[href]').forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('#') && !href.startsWith('javascript:')) {
                const resolvedPath = resolvePath(href);
                link.setAttribute('href', resolvedPath);
                link.setAttribute('data-original-href', href);
            }
        });
        
        // Fix all <link> tags (CSS)
        document.querySelectorAll('link[href]').forEach(link => {
            const href = link.getAttribute('href');
            if (href && !href.startsWith('http') && !href.startsWith('file://')) {
                const resolvedPath = resolvePath(href);
                link.setAttribute('href', resolvedPath);
            }
        });
        
        // Fix all <script> tags
        document.querySelectorAll('script[src]').forEach(script => {
            const src = script.getAttribute('src');
            if (src && !src.startsWith('http') && !src.startsWith('file://')) {
                const resolvedPath = resolvePath(src);
                script.setAttribute('src', resolvedPath);
            }
        });
        
        // Fix all <img> tags
        document.querySelectorAll('img[src]').forEach(img => {
            const src = img.getAttribute('src');
            if (src && !src.startsWith('http') && !src.startsWith('file://') && !src.startsWith('data:')) {
                const resolvedPath = resolvePath(src);
                img.setAttribute('src', resolvedPath);
            }
        });
        
        console.log('All paths resolved for file:// mode');
    }
    
    /**
     * Create a global helper function for dynamic path resolution
     */
    window.resolveTrainingPath = function(relativePath) {
        return resolvePath(relativePath);
    };
    
    /**
     * Get the base path for the training site
     */
    window.getTrainingBasePath = function() {
        return getBasePath();
    };
    
    // Fix paths when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixAllPaths);
    } else {
        fixAllPaths();
    }
    
    // Also fix paths immediately for early-loaded resources
    fixAllPaths();
    
})();
