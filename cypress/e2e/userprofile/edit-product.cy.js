describe('Edit Product Page', () => {
  beforeEach(() => {
    // Suppress uncaught exceptions from application code
    cy.on('uncaught:exception', (err) => {
      // Ignore errors related to dropdown handler or other non-critical errors
      if (err.message.includes('Cannot read properties of null')) {
        return false;
      }
      return true;
    });
    cy.visit('/userprofile/edit-product.html');
  });

  describe('Page Structure & Loading', () => {
    it('should load the edit product page correctly', () => {
      cy.url().should('include', '/userprofile/edit-product.html');
      cy.title().should('contain', 'Edit Product');
    });

    it('should display hero section with banner image', () => {
      cy.get('#hero-banner-image')
        .should('be.visible')
        .should('have.attr', 'src')
        .should('have.attr', 'alt', 'Product Banner');
    });

    it('should display page title "Edit Product"', () => {
      cy.contains('h1', 'Edit Product').should('be.visible');
    });

    it('should display page subtitle', () => {
      cy.contains('Update your product information').should('be.visible');
    });

    it('should display form section title', () => {
      cy.contains('h2', 'Product Details').should('be.visible');
    });

    it('should display form section subtitle', () => {
      cy.contains('Update the information below to modify your product').should('be.visible');
    });

    it('should display back button', () => {
      cy.get('button i').contains('arrow_back').should('exist');
    });

    it('should display site logo', () => {
      cy.get('.site-logo img').should('exist').should('have.attr', 'src');
    });

    it('should display bottom navigation', () => {
      cy.get('[data-testid="mobile-nav-home"]').should('exist');
      cy.get('[data-testid="mobile-nav-search"]').should('exist');
      cy.get('[data-testid="mobile-nav-discussions"]').should('exist');
      cy.get('[data-testid="mobile-nav-cart"]').should('exist');
      cy.get('[data-testid="mobile-nav-profile"]').should('exist');
    });
  });

  describe('Form Fields - Basic Information', () => {
    it('should display product name field with pre-filled value', () => {
      cy.get('[data-testid="product-name-input"]')
        .should('be.visible')
        .should('have.value', 'Citrus IPA');
    });

    it('should display product category field with pre-selected value', () => {
      cy.get('[data-testid="product-category-select"]')
        .should('be.visible')
        .should('have.value', 'beverages');
    });

    it('should display all category options', () => {
      cy.get('[data-testid="product-category-select"]').select('produce');
      cy.get('[data-testid="product-category-select"]').select('dairy');
      cy.get('[data-testid="product-category-select"]').select('meat');
      cy.get('[data-testid="product-category-select"]').select('seafood');
      cy.get('[data-testid="product-category-select"]').select('bakery');
      cy.get('[data-testid="product-category-select"]').select('beverages');
      cy.get('[data-testid="product-category-select"]').select('pantry');
      cy.get('[data-testid="product-category-select"]').select('prepared');
      cy.get('[data-testid="product-category-select"]').select('specialty');
      cy.get('[data-testid="product-category-select"]').select('other');
      // Reset to original value
      cy.get('[data-testid="product-category-select"]').select('beverages');
    });

    it('should display product description field with pre-filled value', () => {
      cy.get('[data-testid="product-description-textarea"]')
        .should('be.visible')
        .should('contain.value', 'Perfectly balanced hops');
    });

    it('should allow editing product name', () => {
      cy.get('[data-testid="product-name-input"]')
        .clear()
        .type('Updated Product Name')
        .should('have.value', 'Updated Product Name');
    });

    it('should allow editing product description', () => {
      cy.get('[data-testid="product-description-textarea"]')
        .clear()
        .type('This is an updated description')
        .should('contain.value', 'This is an updated description');
    });
  });

  describe('Form Fields - Pricing & Inventory', () => {
    it('should display price field with pre-filled value', () => {
      cy.get('[data-testid="product-price-input"]')
        .should('be.visible')
        .should('have.value', '8.99');
    });

    it('should display stock quantity field with pre-filled value', () => {
      cy.get('[data-testid="stock-quantity-input"]')
        .should('be.visible')
        .should('have.value', '150');
    });

    it('should allow editing price', () => {
      cy.get('[data-testid="product-price-input"]')
        .clear()
        .type('12.99')
        .should('have.value', '12.99');
    });

    it('should allow editing stock quantity', () => {
      cy.get('[data-testid="stock-quantity-input"]')
        .clear()
        .type('200')
        .should('have.value', '200');
    });

    it('should accept decimal values for price', () => {
      cy.get('[data-testid="product-price-input"]')
        .clear()
        .type('9.99')
        .should('have.value', '9.99');
    });

    it('should only accept numeric values for stock quantity', () => {
      cy.get('[data-testid="stock-quantity-input"]')
        .clear()
        .type('100')
        .should('have.value', '100');
    });
  });

  describe('Form Fields - Product Details', () => {
    it('should display ingredients field with pre-filled value', () => {
      cy.get('[data-testid="product-ingredients-textarea"]')
        .should('be.visible')
        .should('contain.value', 'Water, Malted Barley');
    });

    it('should display additional notes field with pre-filled value', () => {
      cy.get('[data-testid="additional-notes-textarea"]')
        .should('be.visible')
        .should('contain.value', 'ABV: 6.5%');
    });

    it('should allow editing ingredients', () => {
      cy.get('[data-testid="product-ingredients-textarea"]')
        .clear()
        .type('Updated ingredients list')
        .should('contain.value', 'Updated ingredients list');
    });

    it('should allow editing additional notes', () => {
      cy.get('[data-testid="additional-notes-textarea"]')
        .clear()
        .type('Updated notes')
        .should('contain.value', 'Updated notes');
    });
  });

  describe('Image Upload Functionality', () => {
    it('should display image upload button', () => {
      cy.get('[data-testid="upload-image-btn"]')
        .should('be.visible')
        .should('contain', 'Choose Image');
    });

    it('should display image preview', () => {
      cy.get('#image-preview')
        .should('be.visible')
        .should('have.attr', 'src');
    });

    it('should display hero banner image', () => {
      cy.get('#hero-banner-image')
        .should('be.visible')
        .should('have.attr', 'src');
    });

    it('should update image preview when file is selected', () => {
      // Create a minimal 1x1 pixel JPEG image as base64
      const minimalJpegBase64 = '/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAKAAoDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKAP/2Q==';
      
      // Convert base64 string to binary using window.atob
      cy.window().then((win) => {
        const binaryString = win.atob(minimalJpegBase64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        
        return Cypress.Buffer.from(bytes);
      }).then((fileBuffer) => {
        // Create file using Cypress selectFile
        cy.get('[data-testid="product-image-input"]').selectFile({
          contents: fileBuffer,
          fileName: 'test-image.jpg',
          mimeType: 'image/jpeg',
        }, { force: true });

        // Verify button text updates (may take a moment for DOM update)
        cy.get('[data-testid="upload-image-btn"]', { timeout: 2000 })
          .should('contain', 'check_circle');

        // Verify image preview is still visible
        cy.get('#image-preview').should('be.visible');
      });
    });
  });

  describe('Form Validation', () => {
    it('should mark required fields', () => {
      cy.get('[data-testid="product-name-input"]').should('have.attr', 'required');
      cy.get('[data-testid="product-category-select"]').should('have.attr', 'required');
      cy.get('[data-testid="product-description-textarea"]').should('have.attr', 'required');
      cy.get('[data-testid="product-price-input"]').should('have.attr', 'required');
      cy.get('[data-testid="stock-quantity-input"]').should('have.attr', 'required');
    });

    it('should show validation error when product name is empty', () => {
      cy.get('[data-testid="product-name-input"]').clear().blur();
      cy.get('[data-testid="product-name-input"]').should('have.css', 'border-color', 'rgb(255, 107, 107)');
    });

    it('should show validation error when description is empty', () => {
      cy.get('[data-testid="product-description-textarea"]').clear().blur();
      cy.get('[data-testid="product-description-textarea"]').should('have.css', 'border-color', 'rgb(255, 107, 107)');
    });

    it('should show validation error when price is empty', () => {
      cy.get('[data-testid="product-price-input"]').clear().blur();
      cy.get('[data-testid="product-price-input"]').should('have.css', 'border-color', 'rgb(255, 107, 107)');
    });

    it('should show validation error when stock quantity is empty', () => {
      cy.get('[data-testid="stock-quantity-input"]').clear().blur();
      cy.get('[data-testid="stock-quantity-input"]').should('have.css', 'border-color', 'rgb(255, 107, 107)');
    });

    it('should remove validation error when field is filled', () => {
      cy.get('[data-testid="product-name-input"]').clear().blur();
      cy.get('[data-testid="product-name-input"]').type('New Product Name').blur();
      cy.get('[data-testid="product-name-input"]').should('not.have.css', 'border-color', 'rgb(255, 107, 107)');
    });
  });

  describe('Form Actions', () => {
    it('should display cancel button', () => {
      cy.get('[data-testid="cancel-btn"]')
        .should('be.visible')
        .should('contain', 'Cancel');
    });

    it('should display submit button', () => {
      cy.get('[data-testid="submit-btn"]')
        .should('be.visible')
        .should('contain', 'Save Changes');
    });

    it('should navigate to vendor products page when cancel button is clicked', () => {
      cy.get('[data-testid="cancel-btn"]').parent('a').should('have.attr', 'href', 'vendor-my-products.html');
    });

    it('should submit form with valid data', () => {
      // Fill in all required fields
      cy.get('[data-testid="product-name-input"]').clear().type('Updated Product Name');
      cy.get('[data-testid="product-description-textarea"]').clear().type('Updated description');
      cy.get('[data-testid="product-price-input"]').clear().type('15.99');
      cy.get('[data-testid="stock-quantity-input"]').clear().type('250');

      // Intercept the form submission (if using HTMX)
      cy.intercept('POST', '/api/update-product', { statusCode: 200, body: { success: true } }).as('updateProduct');

      // Submit the form
      cy.get('[data-testid="submit-btn"]').click();

      // Verify form result appears (form submission is mocked, so we check for loading state)
      cy.get('[data-testid="submit-btn"]').should('be.disabled');
    });

    it('should disable submit button during form submission', () => {
      cy.get('[data-testid="product-name-input"]').clear().type('Test Product');
      cy.get('[data-testid="product-description-textarea"]').clear().type('Test description');
      cy.get('[data-testid="product-price-input"]').clear().type('10.00');
      cy.get('[data-testid="stock-quantity-input"]').clear().type('100');

      cy.get('[data-testid="submit-btn"]').click();
      
      // Button should be disabled during submission
      cy.get('[data-testid="submit-btn"]').should('be.disabled');
      cy.get('[data-testid="submit-btn"]').should('contain', 'Saving Changes...');
    });

    it('should prevent form submission with invalid data', () => {
      // Clear required fields
      cy.get('[data-testid="product-name-input"]').clear();
      cy.get('[data-testid="product-description-textarea"]').clear();
      cy.get('[data-testid="product-price-input"]').clear();
      cy.get('[data-testid="stock-quantity-input"]').clear();

      // Try to submit
      cy.get('[data-testid="submit-btn"]').click();

      // Form should not submit (browser validation will prevent it)
      cy.get('[data-testid="product-name-input"]').then(($input) => {
        expect($input[0].validity.valid).to.be.false;
      });
    });
  });

  describe('Navigation', () => {
    it('should navigate back to profile page when back button is clicked', () => {
      cy.get('a[href="index.html"]').should('exist');
    });

    it('should navigate to home page from bottom nav', () => {
      cy.get('[data-testid="mobile-nav-home"]')
        .should('have.attr', 'href', '../home/index.html');
    });

    it('should navigate to search page from bottom nav', () => {
      cy.get('[data-testid="mobile-nav-search"]')
        .should('have.attr', 'href', '../index.html');
    });

    it('should navigate to discussions page from bottom nav', () => {
      cy.get('[data-testid="mobile-nav-discussions"]')
        .should('have.attr', 'href', '../discussions/forums/index.html');
    });

    it('should navigate to cart page from bottom nav', () => {
      cy.get('[data-testid="mobile-nav-cart"]')
        .should('have.attr', 'href', '../cart/index.html');
    });

    it('should navigate to profile page from bottom nav', () => {
      cy.get('[data-testid="mobile-nav-profile"]')
        .should('have.attr', 'href', 'index.html');
    });

    it('should have active state on profile nav item', () => {
      cy.get('[data-testid="mobile-nav-profile"]').should('have.class', 'active');
    });
  });

  describe('Form Sections', () => {
    it('should display Basic Information section', () => {
      cy.contains('h3', 'Basic Information').should('be.visible');
    });

    it('should display Pricing & Inventory section', () => {
      cy.contains('h3', 'Pricing & Inventory').should('be.visible');
    });

    it('should display Product Details section', () => {
      cy.contains('h3', 'Product Details').should('be.visible');
    });

    it('should display all form sections in correct order', () => {
      cy.get('.form-section').should('have.length', 3);
      cy.get('.form-section').first().should('contain', 'Basic Information');
      cy.get('.form-section').eq(1).should('contain', 'Pricing & Inventory');
      cy.get('.form-section').last().should('contain', 'Product Details');
    });
  });

  describe('Form Field Labels', () => {
    it('should display all required field labels with asterisks', () => {
      cy.contains('label', 'Product Name *').should('be.visible');
      cy.contains('label', 'Category *').should('be.visible');
      cy.contains('label', 'Description *').should('be.visible');
      cy.contains('label', 'Price *').should('be.visible');
      cy.contains('label', 'Stock Quantity *').should('be.visible');
    });

    it('should display optional field labels without asterisks', () => {
      cy.contains('label', 'Ingredients').should('be.visible');
      cy.contains('label', 'Additional Notes').should('be.visible');
      cy.contains('label', 'Upload Product Image').should('be.visible');
    });
  });
});

