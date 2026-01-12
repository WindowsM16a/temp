// ================= MOBILE MENU TOGGLE =================
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    const navLinksItems = document.querySelectorAll('.nav-links a');
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Toggle active class on hamburger
            this.classList.toggle('active');
            
            // Toggle active class on nav links
            navLinks.classList.toggle('active');
            
            // Toggle body class to prevent scrolling
            document.body.classList.toggle('menu-open');
        });
        
        // Close menu when clicking on a link
        navLinksItems.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navLinks.contains(e.target) && !hamburger.contains(e.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
        
        // Close menu on window resize (if resized to desktop)
        window.addEventListener('resize', function() {
            if (window.innerWidth > 768) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }
    
    // ================= DROPDOWN TOGGLE =================
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    let activeDropdown = null;
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.parentElement;
            const dropdownMenu = this.nextElementSibling;
            
            // Close other dropdowns
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                if (menu !== dropdownMenu) {
                    menu.classList.remove('active');
                    menu.parentElement.classList.remove('active');
                }
            });
            
            // Toggle current dropdown
            dropdownMenu.classList.toggle('active');
            dropdown.classList.toggle('active');
            
            // Update active dropdown reference
            activeDropdown = dropdownMenu.classList.contains('active') ? dropdownMenu : null;
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('active');
            });
            activeDropdown = null;
        }
    });
    
    // Close dropdowns on window resize
    window.addEventListener('resize', function() {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.remove('active');
        });
        activeDropdown = null;
    });

    // ================= NAVIGATION STATE MANAGEMENT =================
    // Initialize navigation state
    function initializeNavState() {
        const currentPath = window.location.pathname;
        
        // Check if we're on a sub-page (not dashboard)
        if (!currentPath.includes('/dashboard/') || currentPath === '/dashboard/employee/') {
            // Determine which dropdown should be visible based on current URL
            let activeDropdown = null;
            
            if (currentPath.includes('/customers') || currentPath.includes('/cars')) {
                activeDropdown = 'fleet';
            } else if (currentPath.includes('/rentals') || currentPath.includes('/payments')) {
                activeDropdown = 'operations';
            } else if (currentPath.includes('/maintenances') || currentPath.includes('/reservations')) {
                activeDropdown = 'services';
            }
            
            if (activeDropdown) {
                handleNavClick(activeDropdown);
            } else {
                showFullNavbar();
            }
        } else {
            showFullNavbar();
        }
    }
    
    // Function to handle navigation clicks
    window.handleNavClick = function(dropdownType) {
        // Hide all nav items except dashboard and the clicked dropdown type
        document.querySelectorAll('.nav-item').forEach(item => {
            if (!item.classList.contains('dashboard-item') && 
                !item.classList.contains(dropdownType + '-dropdown')) {
                item.classList.add('hidden');
            }
        });
        
        // Show back button
        document.querySelector('.back-button').style.display = 'inline-block';
        
        // Close any open dropdowns
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.classList.remove('active');
        });
        document.querySelectorAll('.dropdown').forEach(dropdown => {
            dropdown.classList.remove('active');
        });
        activeDropdown = null;
    };

    // Function to show table content
    window.showTable = function(tableType) {
        // Hide all table contents
        document.querySelectorAll('.table-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById('dashboard-content').style.display = 'none';
        
        // Show the selected table
        if (tableType === 'dashboard') {
            document.getElementById('dashboard-content').style.display = 'block';
            showFullNavbar();
        } else {
            const tableContent = document.getElementById(tableType + '-content');
            if (tableContent) {
                tableContent.style.display = 'block';
            }
            
            // Determine dropdown type
            let dropdownType = '';
            if (['cars', 'customers'].includes(tableType)) {
                dropdownType = 'fleet';
            } else if (['rentals', 'payments'].includes(tableType)) {
                dropdownType = 'operations';
            } else if (['maintenance', 'reservations'].includes(tableType)) {
                dropdownType = 'services';
            }
            
            // Handle navbar
            if (dropdownType) {
                handleNavClick(dropdownType);
            } else {
                showFullNavbar();
            }
        }
    };

    // Function to show full navbar
    window.showFullNavbar = function() {
        // Show all nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('hidden');
        });
        
        // Hide back button
        document.querySelector('.back-button').style.display = 'none';
    };

    // Initialize navigation state on page load
    initializeNavState();
    
    // Show dashboard by default
    showTable('dashboard');

    // ================= FORM VALIDATION =================
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Create error message if not exists
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.className = 'error-message';
                        errorMsg.textContent = 'This field is required';
                        errorMsg.style.color = 'var(--danger)';
                        errorMsg.style.fontSize = '0.85rem';
                        errorMsg.style.marginTop = '0.25rem';
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                } else {
                    field.classList.remove('error');
                    const errorMsg = field.nextElementSibling;
                    if (errorMsg && errorMsg.classList.contains('error-message')) {
                        errorMsg.remove();
                    }
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Scroll to first error
                const firstError = form.querySelector('.error');
                if (firstError) {
                    firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
        
        // Clear error on input
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('error');
                const errorMsg = this.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            });
        });
    });
    
    // ================= ACTIVE NAV LINK HIGHLIGHTING =================
    const currentPage = window.location.pathname;
    navLinksItems.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPage.includes(linkPath) && linkPath !== '/') {
            link.classList.add('active');
        }
    });

    // ================= MAINTENANCE FORM ENHANCEMENTS =================
    // Auto-format cost fields
    const costFields = ['id_cost', 'id_labor_cost', 'id_parts_cost', 'id_tax_amount'];
    
    costFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('blur', function() {
                if (this.value && !isNaN(this.value)) {
                    this.value = parseFloat(this.value).toFixed(2);
                }
            });
            
            field.addEventListener('input', function() {
                // Allow only numbers and decimal point
                this.value = this.value.replace(/[^0-9.]/g, '');
                
                // Prevent multiple decimal points
                if ((this.value.match(/\./g) || []).length > 1) {
                    this.value = this.value.substring(0, this.value.lastIndexOf('.'));
                }
            });
        }
    });

    // Auto-calculate total cost from labor and parts
    const laborCostField = document.getElementById('id_labor_cost');
    const partsCostField = document.getElementById('id_parts_cost');
    const totalCostField = document.getElementById('id_cost');
    const taxField = document.getElementById('id_tax_amount');

    function calculateTotalCost() {
        if (laborCostField && partsCostField && totalCostField) {
            const labor = parseFloat(laborCostField.value) || 0;
            const parts = parseFloat(partsCostField.value) || 0;
            const tax = parseFloat(taxField.value) || 0;
            
            const total = labor + parts + tax;
            if (totalCostField && !isNaN(total)) {
                totalCostField.value = total.toFixed(2);
            }
        }
    }

    if (laborCostField) laborCostField.addEventListener('input', calculateTotalCost);
    if (partsCostField) partsCostField.addEventListener('input', calculateTotalCost);
    if (taxField) taxField.addEventListener('input', calculateTotalCost);

    // Auto-calculate warranty expiry date
    const warrantyPeriodField = document.getElementById('id_warranty_period');
    const completedDateField = document.getElementById('id_completed_date');
    const warrantyExpiryField = document.getElementById('id_warranty_expiry_date');

    function calculateWarrantyExpiry() {
        if (warrantyPeriodField && completedDateField && warrantyExpiryField) {
            const period = parseInt(warrantyPeriodField.value) || 0;
            const completedDate = completedDateField.value;
            
            if (period > 0 && completedDate) {
                const completed = new Date(completedDate);
                completed.setDate(completed.getDate() + period);
                
                // Format date as YYYY-MM-DD
                const year = completed.getFullYear();
                const month = String(completed.getMonth() + 1).padStart(2, '0');
                const day = String(completed.getDate()).padStart(2, '0');
                
                warrantyExpiryField.value = `${year}-${month}-${day}`;
            }
        }
    }

    if (warrantyPeriodField) warrantyPeriodField.addEventListener('input', calculateWarrantyExpiry);
    if (completedDateField) completedDateField.addEventListener('change', calculateWarrantyExpiry);

    // Auto-calculate next service date
    const serviceTypeField = document.getElementById('id_service_type');
    const scheduledDateField = document.getElementById('id_scheduled_date');
    const completedDateField2 = document.getElementById('id_completed_date');
    const nextServiceDateField = document.getElementById('id_next_service_date');
    const nextServiceMileageField = document.getElementById('id_next_service_mileage');
    const mileageField = document.getElementById('id_mileage_at_service');

    function calculateNextService() {
        if (serviceTypeField && (completedDateField2 || scheduledDateField)) {
            const serviceType = serviceTypeField.value;
            const dateField = completedDateField2.value ? completedDateField2 : scheduledDateField;
            const baseDate = dateField.value;
            
            if (baseDate) {
                const date = new Date(baseDate);
                const mileage = parseInt(mileageField.value) || 0;
                
                // Calculate next service based on type
                let nextDate = new Date(date);
                let nextMileage = mileage;
                
                const quickServices = ['oil_change', 'tire_rotation', 'general_service'];
                const majorServices = ['brake_service', 'engine_tune', 'transmission', 'suspension'];
                
                if (quickServices.includes(serviceType)) {
                    // Quick services: 6 months
                    nextDate.setMonth(nextDate.getMonth() + 6);
                    nextMileage += 5000;
                } else if (majorServices.includes(serviceType)) {
                    // Major services: 1 year
                    nextDate.setFullYear(nextDate.getFullYear() + 1);
                    nextMileage += 10000;
                } else {
                    // Other services: 8 months
                    nextDate.setMonth(nextDate.getMonth() + 8);
                    nextMileage += 7500;
                }
                
                // Format date as YYYY-MM-DD
                const year = nextDate.getFullYear();
                const month = String(nextDate.getMonth() + 1).padStart(2, '0');
                const day = String(nextDate.getDate()).padStart(2, '0');
                
                if (nextServiceDateField) {
                    nextServiceDateField.value = `${year}-${month}-${day}`;
                }
                
                if (nextServiceMileageField && mileage > 0) {
                    nextServiceMileageField.value = nextMileage;
                }
            }
        }
    }

    if (serviceTypeField) serviceTypeField.addEventListener('change', calculateNextService);
    if (completedDateField2) completedDateField2.addEventListener('change', calculateNextService);
    if (mileageField) mileageField.addEventListener('input', calculateNextService);

    // Auto-format mileage fields
    const mileageFields = ['id_mileage_at_service', 'id_next_service_mileage'];
    
    mileageFields.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener('input', function() {
                // Allow only numbers
                this.value = this.value.replace(/\D/g, '');
                
                // Add thousand separators
                if (this.value.length > 3) {
                    let num = this.value.replace(/,/g, '');
                    num = parseInt(num).toLocaleString();
                    this.value = num;
                }
            });
        }
    });

    // Auto-populate title based on service type
    if (serviceTypeField) {
        const titleField = document.getElementById('id_title');
        
        if (titleField) {
            serviceTypeField.addEventListener('change', function() {
                if (!titleField.value || titleField.value === 'General Maintenance Service') {
                    const selectedOption = serviceTypeField.options[serviceTypeField.selectedIndex];
                    if (selectedOption.text !== '---------') {
                        titleField.value = selectedOption.text;
                    }
                }
            });
        }
    }

    // Date validation - ensure completed date is not before scheduled date
    if (scheduledDateField && completedDateField2) {
        completedDateField2.addEventListener('change', function() {
            const scheduled = new Date(scheduledDateField.value);
            const completed = new Date(this.value);
            
            if (completed < scheduled) {
                alert('Completed date cannot be before scheduled date!');
                this.value = '';
            }
        });
    }

    // Add character counter for text areas
    const textAreas = document.querySelectorAll('textarea');
    textAreas.forEach(textarea => {
        const container = textarea.closest('div');
        const counter = document.createElement('div');
        counter.className = 'char-counter';
        counter.style.fontSize = '12px';
        counter.style.color = '#7f8c8d';
        counter.style.marginTop = '5px';
        container.appendChild(counter);

        function updateCounter() {
            const length = textarea.value.length;
            const maxLength = textarea.maxLength || 1000;
            counter.textContent = `${length}/${maxLength} characters`;
            
            if (length > maxLength * 0.9) {
                counter.style.color = '#e74c3c';
            } else if (length > maxLength * 0.75) {
                counter.style.color = '#f39c12';
            } else {
                counter.style.color = '#7f8c8d';
            }
        }

        textarea.addEventListener('input', updateCounter);
        updateCounter(); // Initial update
    });

    // ================= PAYMENT FORM ENHANCEMENTS =================
    function setupPaymentForm() {
        const paymentForm = document.querySelector('form[action*="payment"]');
        if (paymentForm) {
            // Setup payment method selection
            const paymentMethodField = paymentForm.querySelector('[name="payment_method"]');
            if (paymentMethodField) {
                const paymentMethods = paymentForm.querySelectorAll('.payment-method');
                
                paymentMethods.forEach(method => {
                    method.addEventListener('click', function() {
                        // Remove selected from all methods
                        paymentMethods.forEach(m => m.classList.remove('selected'));
                        
                        // Add selected to clicked method
                        this.classList.add('selected');
                        
                        // Update hidden field
                        const methodValue = this.dataset.value;
                        paymentMethodField.value = methodValue;
                        
                        // Update payment summary
                        updatePaymentSummary();
                    });
                    
                    // Check if this method matches current value
                    if (method.dataset.value === paymentMethodField.value) {
                        method.classList.add('selected');
                    }
                });
            }
            
            // Setup amount calculation
            const amountField = paymentForm.querySelector('[name="amount"]');
            const rentalSelect = paymentForm.querySelector('[name="rental"]');
            
            function updatePaymentSummary() {
                const amount = parseFloat(amountField.value) || 0;
                const method = paymentMethodField.value || 'cash';
                const today = new Date().toLocaleDateString();
                
                // Update summary if container exists
                const summaryContainer = document.querySelector('.payment-summary');
                if (summaryContainer) {
                    summaryContainer.innerHTML = `
                        <h4><i class="fas fa-file-invoice-dollar"></i> Payment Summary</h4>
                        <div class="summary-row">
                            <span>Amount:</span>
                            <span>₵${amount.toFixed(2)}</span>
                        </div>
                        <div class="summary-row">
                            <span>Payment Method:</span>
                            <span>${method.charAt(0).toUpperCase() + method.slice(1)}</span>
                        </div>
                        <div class="summary-row">
                            <span>Date:</span>
                            <span>${today}</span>
                        </div>
                        <div class="summary-row total">
                            <span>Total to Pay:</span>
                            <span>₵${amount.toFixed(2)}</span>
                        </div>
                    `;
                }
            }
            
            // Listen for changes
            if (amountField) amountField.addEventListener('input', updatePaymentSummary);
            if (paymentMethodField) paymentMethodField.addEventListener('change', updatePaymentSummary);
            
            // Initial update
            if (amountField && paymentMethodField) {
                updatePaymentSummary();
            }
            
            // Auto-fill amount from rental
            if (rentalSelect && amountField) {
                rentalSelect.addEventListener('change', function() {
                    const selectedOption = this.options[this.selectedIndex];
                    const rentalAmount = selectedOption.dataset.amount || 0;
                    
                    if (rentalAmount > 0 && !amountField.value) {
                        amountField.value = parseFloat(rentalAmount).toFixed(2);
                        updatePaymentSummary();
                    }
                });
            }
        }
    }

    // ================= RESERVATION FORM ENHANCEMENTS =================
    function setupReservationForm() {
        const reservationForm = document.querySelector('form[action*="reservation"]');
        if (reservationForm) {
            // Setup date validation
            const startDateField = reservationForm.querySelector('[name="start_date"]');
            const endDateField = reservationForm.querySelector('[name="end_date"]');
            
            if (startDateField && endDateField) {
                startDateField.addEventListener('change', function() {
                    if (endDateField.value) {
                        const endDate = new Date(endDateField.value);
                        const startDate = new Date(this.value);
                        
                        if (endDate < startDate) {
                            endDateField.value = '';
                        }
                    }
                });
            }
        }
    }

    // Initialize all form enhancements
    setupPaymentForm();
    setupReservationForm();

    // ================= DROPDOWN MENUS =================
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // Close other dropdowns
                dropdowns.forEach(other => {
                    if (other !== dropdown) {
                        other.classList.remove('open');
                    }
                });
                
                // Toggle current dropdown
                dropdown.classList.toggle('open');
            });
        }
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function() {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('open');
        });
    });

    // ================= ACCORDION FUNCTIONALITY =================
    const accordionToggles = document.querySelectorAll('.accordion-toggle');
    
    accordionToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const accordion = this.closest('.accordion');
            const content = this.nextElementSibling;
            
            // Toggle current accordion
            accordion.classList.toggle('active');
            
            // Animate content
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + 'px';
            }
        });
    });

    // ================= TAB FUNCTIONALITY =================
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show corresponding content
            const activeContent = document.getElementById(tabId);
            if (activeContent) {
                activeContent.classList.add('active');
            }
        });
    });

    // ================= SORTABLE TABLES =================
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentNode.children).indexOf(this);
            const sortDirection = this.classList.contains('asc') ? -1 : 1;
            
            // Clear other sort indicators
            sortableHeaders.forEach(h => {
                h.classList.remove('asc', 'desc');
            });
            
            // Set new sort indicator
            this.classList.toggle('asc', sortDirection === -1);
            this.classList.toggle('desc', sortDirection === 1);
            
            // Sort rows
            rows.sort((a, b) => {
                const aText = a.children[columnIndex].textContent.trim();
                const bText = b.children[columnIndex].textContent.trim();
                
                // Try to sort as numbers
                const aNum = parseFloat(aText);
                const bNum = parseFloat(bText);
                
                if (!isNaN(aNum) && !isNaN(bNum)) {
                    return (aNum - bNum) * sortDirection;
                }
                
                // Sort as text
                return aText.localeCompare(bText) * sortDirection;
            });
            
            // Reappend rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });

    // ================= TOOLTIPS =================
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.getAttribute('data-tooltip');
        document.body.appendChild(tooltip);
        
        element.addEventListener('mouseenter', function(e) {
            const rect = this.getBoundingClientRect();
            tooltip.style.left = (rect.left + rect.width / 2) + 'px';
            tooltip.style.top = (rect.top - 40) + 'px';
            tooltip.classList.add('active');
        });
        
        element.addEventListener('mouseleave', function() {
            tooltip.classList.remove('active');
        });
    });

    // ================= COPY TO CLIPBOARD =================
    const copyButtons = document.querySelectorAll('[data-copy]');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            navigator.clipboard.writeText(textToCopy).then(() => {
                // Show success feedback
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                this.classList.add('success');
                
                setTimeout(() => {
                    this.innerHTML = originalText;
                    this.classList.remove('success');
                }, 2000);
            });
        });
    });

    // ================= KEYBOARD SHORTCUTS =================
    document.addEventListener('keydown', function(e) {
        // Ctrl+S to save forms
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.click();
            }
        }
        
        // Esc to close mobile menu
        if (e.key === 'Escape') {
            if (hamburger && navLinks) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        }
    });
});

 document.addEventListener('DOMContentLoaded', function() {
            // Password toggle
            const togglePassword = document.getElementById('togglePassword');
            const passwordField = document.getElementById('id_password');
            
            if (togglePassword && passwordField) {
                togglePassword.addEventListener('click', function() {
                    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
                    passwordField.setAttribute('type', type);
                    this.classList.toggle('fa-eye');
                    this.classList.toggle('fa-eye-slash');
                });
            }

            // User type selection with checkboxes
            const userTypeOptions = document.querySelectorAll('.user-type-option');
            userTypeOptions.forEach(option => {
                option.addEventListener('click', function(e) {
                    // Don't trigger if clicking directly on checkbox
                    if (e.target.type === 'checkbox') return;

                    const checkbox = this.querySelector('input[type="checkbox"]');
                    if (checkbox) {
                        // For login form, allow only one selection (like radio behavior)
                        if (!checkbox.checked) {
                            // Uncheck all other checkboxes
                            userTypeOptions.forEach(opt => {
                                const otherCheckbox = opt.querySelector('input[type="checkbox"]');
                                if (otherCheckbox && otherCheckbox !== checkbox) {
                                    otherCheckbox.checked = false;
                                    opt.classList.remove('selected');
                                }
                            });
                            // Check this one
                            checkbox.checked = true;
                            this.classList.add('selected');
                        } else {
                            // Allow unchecking if it's already checked
                            checkbox.checked = false;
                            this.classList.remove('selected');
                        }
                    }
                });
            });

            // Also handle direct checkbox clicks
            const checkboxes = document.querySelectorAll('.user-type-option input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    const option = this.closest('.user-type-option');
                    if (this.checked) {
                        // Uncheck others and update classes
                        checkboxes.forEach(otherCheckbox => {
                            if (otherCheckbox !== this) {
                                otherCheckbox.checked = false;
                                otherCheckbox.closest('.user-type-option').classList.remove('selected');
                            }
                        });
                        option.classList.add('selected');
                    } else {
                        option.classList.remove('selected');
                    }
                });
            });

            // Form submission loading state
            const loginForm = document.getElementById('loginForm');
            const loginButton = document.getElementById('loginButton');
            
            if (loginForm && loginButton) {
                loginForm.addEventListener('submit', function() {
                    loginButton.classList.add('loading');
                    loginButton.disabled = true;
                });
            }

            // Auto-focus email field
            const emailField = document.getElementById('id_username');
            if (emailField) {
                emailField.focus();
            }

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter to submit form
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    loginForm.submit();
                }
                
                // Escape to clear form
                if (e.key === 'Escape') {
                    loginForm.reset();
                    userTypeOptions.forEach(opt => opt.classList.remove('selected'));
                    if (emailField) emailField.focus();
                }
            });

            // Remember me functionality
            const rememberCheckbox = document.getElementById('remember');
            if (rememberCheckbox) {
                // Check if there's saved email
                const savedEmail = localStorage.getItem('saved_email');
                if (savedEmail && emailField) {
                    emailField.value = savedEmail;
                    rememberCheckbox.checked = true;
                }

                // Save email on form submission if remember me is checked
                loginForm.addEventListener('submit', function() {
                    if (rememberCheckbox.checked && emailField && emailField.value) {
                        localStorage.setItem('saved_email', emailField.value);
                    } else {
                        localStorage.removeItem('saved_email');
                    }
                });
            }
        });

// ================= SEARCH AND FILTER FUNCTIONALITY =================
document.addEventListener('DOMContentLoaded', function() {
    // Search functionality for customers
    const customerSearchForm = document.querySelector('#customers-content .search-form');
    if (customerSearchForm) {
        customerSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[name="q"]').value.toLowerCase();
            const rows = document.querySelectorAll('#customers-content tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }

    // Filter functionality for cars
    const carFilterForm = document.querySelector('#cars-content .filter-form');
    if (carFilterForm) {
        carFilterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const status = this.querySelector('select[name="status"]').value.toLowerCase();
            const rows = document.querySelectorAll('#cars-content tbody tr');
            
            rows.forEach(row => {
                const carStatus = row.cells[4].textContent.toLowerCase(); // Status column
                row.style.display = (status === '' || carStatus === status) ? '' : 'none';
            });
        });
    }

    // Search functionality for rentals
    const rentalSearchForm = document.querySelector('#rentals-content .search-form');
    if (rentalSearchForm) {
        rentalSearchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const query = this.querySelector('input[name="q"]').value.toLowerCase();
            const rows = document.querySelectorAll('#rentals-content tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    }
});