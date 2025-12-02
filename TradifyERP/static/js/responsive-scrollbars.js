/**
 * Responsive Scrollbar Manager
 * Dynamically adjusts scrollbar behavior based on:
 * - Browser zoom level (Ctrl+/-, browser zoom)
 * - Viewport width and content width
 * - Device type (mobile, tablet, desktop)
 * - User preferences
 */

(function() {
    'use strict';

    const ScrollbarManager = {
        // Configuration
        config: {
            zoomThreshold: 1.1, // Show prominent scrollbars when zoom > 110%
            checkInterval: 500, // Check every 500ms for zoom changes
            enableHorizontalScroll: true,
            enableVerticalScroll: true,
            detectZoomLevel: true,
        },

        // State
        state: {
            currentZoom: window.devicePixelRatio || 1,
            lastZoom: window.devicePixelRatio || 1,
            hasHorizontalOverflow: false,
            hasVerticalOverflow: false,
        },

        /**
         * Initialize the scrollbar manager
         */
        init: function() {
            console.log('🔄 Initializing Responsive Scrollbar Manager...');

            // Initial check
            this.checkScrollbarNeeds();

            // Monitor zoom changes
            this.monitorZoomChanges();

            // Monitor window resize
            this.monitorWindowResize();

            // Monitor content overflow
            this.monitorContentOverflow();

            // Add event listeners
            this.attachEventListeners();

            console.log('✅ Responsive Scrollbar Manager initialized');
        },

        /**
         * Detect current zoom level
         */
        getZoomLevel: function() {
            // Method 1: Using devicePixelRatio
            if (window.devicePixelRatio) {
                return window.devicePixelRatio;
            }

            // Method 2: Using screen.logicalXDPI and screen.deviceXDPI (IE/Edge)
            if (screen.logicalXDPI && screen.deviceXDPI) {
                return screen.deviceXDPI / screen.logicalXDPI;
            }

            // Method 3: Using getBoundingClientRect
            const testElement = document.createElement('div');
            testElement.style.position = 'absolute';
            testElement.style.width = '1in';
            testElement.style.height = '1in';
            testElement.style.visibility = 'hidden';
            document.body.appendChild(testElement);

            const zoom = (testElement.offsetWidth / 96); // 96 is default DPI
            document.body.removeChild(testElement);

            return zoom || 1;
        },

        /**
         * Check if elements have overflow
         */
        checkScrollbarNeeds: function() {
            // Check main content area
            const mainContent = document.querySelector('.main-content') || document.body;
            const pageContent = document.querySelector('.page-content');
            const tableResponsives = document.querySelectorAll('.table-responsive');

            // Check for horizontal overflow
            this.state.hasHorizontalOverflow = mainContent.scrollWidth > mainContent.clientWidth;

            // Check for vertical overflow
            this.state.hasVerticalOverflow = mainContent.scrollHeight > mainContent.clientHeight;

            // Log overflow status for debugging
            if (this.state.hasHorizontalOverflow || this.state.hasVerticalOverflow) {
                console.log('📊 Overflow detected:', {
                    horizontal: this.state.hasHorizontalOverflow,
                    vertical: this.state.hasVerticalOverflow,
                    width: `${mainContent.scrollWidth}px / ${mainContent.clientWidth}px`,
                    height: `${mainContent.scrollHeight}px / ${mainContent.clientHeight}px`,
                });
            }

            // Ensure tables have horizontal scrolling capability
            tableResponsives.forEach(table => {
                if (table.scrollWidth > table.clientWidth) {
                    table.style.overflowX = 'auto';
                }
            });
        },

        /**
         * Monitor zoom level changes
         */
        monitorZoomChanges: function() {
            const self = this;

            setInterval(() => {
                const newZoom = self.getZoomLevel();

                // Detect zoom change (with small tolerance for floating point)
                if (Math.abs(newZoom - self.state.lastZoom) > 0.01) {
                    console.log(`🔍 Zoom level changed: ${(self.state.lastZoom * 100).toFixed(0)}% → ${(newZoom * 100).toFixed(0)}%`);

                    self.state.currentZoom = newZoom;
                    self.state.lastZoom = newZoom;

                    // Trigger scrollbar adjustment
                    self.adjustScrollbarsForZoom(newZoom);

                    // Store zoom preference
                    self.storeZoomPreference(newZoom);
                }
            }, this.config.checkInterval);
        },

        /**
         * Adjust scrollbars based on zoom level
         */
        adjustScrollbarsForZoom: function(zoomLevel) {
            const zoomPercent = zoomLevel * 100;

            if (zoomLevel > this.config.zoomThreshold) {
                console.log(`📈 High zoom detected (${zoomPercent.toFixed(0)}%). Enhancing scrollbar visibility...`);
                this.enhanceScrollbarVisibility();
            } else {
                console.log(`📉 Normal zoom (${zoomPercent.toFixed(0)}%). Using default scrollbars.`);
                this.restoreDefaultScrollbars();
            }
        },

        /**
         * Enhance scrollbar visibility for zoomed views
         */
        enhanceScrollbarVisibility: function() {
            // Add class to body for CSS to apply enhanced scrollbar styles
            document.documentElement.setAttribute('data-scrollbars-enhanced', 'true');
            document.body.setAttribute('data-zoom-level', 'high');
        },

        /**
         * Restore default scrollbars
         */
        restoreDefaultScrollbars: function() {
            document.documentElement.setAttribute('data-scrollbars-enhanced', 'false');
            document.body.setAttribute('data-zoom-level', 'normal');
        },

        /**
         * Monitor window resize events
         */
        monitorWindowResize: function() {
            const self = this;
            let resizeTimeout;

            window.addEventListener('resize', () => {
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(() => {
                    self.checkScrollbarNeeds();
                }, 250);
            });
        },

        /**
         * Monitor content overflow changes
         */
        monitorContentOverflow: function() {
            const self = this;
            const observer = new MutationObserver(() => {
                self.checkScrollbarNeeds();
            });

            const mainContent = document.querySelector('.main-content') || document.body;
            observer.observe(mainContent, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });
        },

        /**
         * Attach event listeners for better scrollbar control
         */
        attachEventListeners: function() {
            const self = this;

            // Listen for page visibility changes
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden) {
                    self.checkScrollbarNeeds();
                }
            });

            // Listen for orientation changes
            window.addEventListener('orientationchange', () => {
                setTimeout(() => self.checkScrollbarNeeds(), 500);
            });

            // Listen for scroll events to track user interaction
            window.addEventListener('scroll', () => {
                this.updateScrollIndicators();
            }, { passive: true });
        },

        /**
         * Update visual indicators for scroll position
         */
        updateScrollIndicators: function() {
            const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;

            // Add attribute for CSS to show scroll progress
            document.documentElement.setAttribute('data-scroll-progress', Math.round(scrollPercent));
        },

        /**
         * Store zoom preference in localStorage
         */
        storeZoomPreference: function(zoomLevel) {
            try {
                localStorage.setItem('userZoomLevel', zoomLevel);
            } catch (e) {
                // localStorage not available
            }
        },

        /**
         * Get stored zoom preference
         */
        getStoredZoomPreference: function() {
            try {
                return parseFloat(localStorage.getItem('userZoomLevel')) || 1;
            } catch (e) {
                return 1;
            }
        },

        /**
         * Force scrollbar visibility check
         */
        forceCheck: function() {
            console.log('🔄 Forcing scrollbar visibility check...');
            this.checkScrollbarNeeds();
            this.adjustScrollbarsForZoom(this.getZoomLevel());
        },

        /**
         * Get scrollbar info for debugging
         */
        getScrollbarInfo: function() {
            const info = {
                zoomLevel: `${(this.state.currentZoom * 100).toFixed(0)}%`,
                hasHorizontalOverflow: this.state.hasHorizontalOverflow,
                hasVerticalOverflow: this.state.hasVerticalOverflow,
                windowWidth: window.innerWidth,
                windowHeight: window.innerHeight,
                documentWidth: document.documentElement.scrollWidth,
                documentHeight: document.documentElement.scrollHeight,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
            };

            console.table(info);
            return info;
        },

        /**
         * Enable keyboard shortcuts for scrolling
         */
        enableKeyboardShortcuts: function() {
            document.addEventListener('keydown', (e) => {
                // Alt+Right Arrow: Scroll right
                if (e.altKey && e.key === 'ArrowRight') {
                    window.scrollBy({ left: 200, behavior: 'smooth' });
                    e.preventDefault();
                }

                // Alt+Left Arrow: Scroll left
                if (e.altKey && e.key === 'ArrowLeft') {
                    window.scrollBy({ left: -200, behavior: 'smooth' });
                    e.preventDefault();
                }

                // Alt+Down Arrow: Scroll down
                if (e.altKey && e.key === 'ArrowDown') {
                    window.scrollBy({ top: 200, behavior: 'smooth' });
                    e.preventDefault();
                }

                // Alt+Up Arrow: Scroll up
                if (e.altKey && e.key === 'ArrowUp') {
                    window.scrollBy({ top: -200, behavior: 'smooth' });
                    e.preventDefault();
                }
            });
        }
    };

    /**
     * Initialize when DOM is ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            ScrollbarManager.init();
            ScrollbarManager.enableKeyboardShortcuts();
        });
    } else {
        ScrollbarManager.init();
        ScrollbarManager.enableKeyboardShortcuts();
    }

    /**
     * Expose ScrollbarManager to window for debugging
     */
    window.ScrollbarManager = ScrollbarManager;

    /**
     * Console commands for debugging
     */
    window.debugScrollbars = function() {
        console.log('📋 Scrollbar Debug Info:');
        ScrollbarManager.getScrollbarInfo();
    };

    window.forceScrollbarCheck = function() {
        ScrollbarManager.forceCheck();
    };
})();
