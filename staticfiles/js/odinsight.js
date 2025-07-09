// Odinsight Application JavaScript

// Global app object
var Odinsight = {
    init: function() {
        console.log('Odinsight Network Automation Platform loaded');
        this.initializeTooltips();
        this.initializeModals();
    },
    
    initializeTooltips: function() {
        // Initialize Bootstrap tooltips
        $('[data-toggle="tooltip"]').tooltip();
    },
    
    initializeModals: function() {
        // Initialize modals
        $('.modal').modal({
            show: false
        });
    },
    
    // Network related functions
    Network: {
        refreshStatus: function() {
            console.log('Refreshing network status...');
            // AJAX call to refresh network status
        }
    },
    
    // Workflow related functions
    Workflow: {
        builder: null,
        initBuilder: function(containerId) {
            console.log('Initializing workflow builder in:', containerId);
            // JointJS+ initialization will go here
        }
    },
    
    // Device related functions
    Device: {
        testConnection: function(deviceId) {
            console.log('Testing connection for device:', deviceId);
            // AJAX call to test device connection
        }
    }
};

// Initialize on document ready
$(document).ready(function() {
    Odinsight.init();
});
