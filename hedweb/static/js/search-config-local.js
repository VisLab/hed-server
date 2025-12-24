/**
 * LOCAL TESTING CONFIGURATION
 * 
 * This version only searches the local hed-web documentation for testing.
 * Use search-config.js for production (searches all HED repositories).
 */

const SEARCH_CONFIG = {
    sources: [
        {
            name: 'HED Web Tools (Local)',
            url: '/hed-web',
            searchIndex: '/static/searchindex.js',  // Local search index
            description: 'Web-based HED tools and REST API',
            priority: 1,
            color: '#0d6efd'
        }
    ],
    
    // Search options
    options: {
        maxResultsPerSource: 20,   // More results for testing
        minScore: 0.05,            // Lower threshold for testing
        highlightTerms: true,
        showPreviews: true,
        previewLength: 150
    }
};
