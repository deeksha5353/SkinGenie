// Product Data
const products = [
    {
        id: 1,
        name: "Natural Glow Foundation",
        category: "foundation",
        price: "$29.99",
        image: "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        description: "Long-lasting foundation for all skin types with natural finish and medium coverage",
        rating: 4.5,
        reviews: 128,
        skinTypes: ["Oily", "Combination", "Dry"],
        coverage: "Medium",
        finish: "Natural",
        brand: "SkinGenie",
        size: "30ml",
        ingredients: ["Water", "Glycerin", "Dimethicone", "Titanium Dioxide", "Iron Oxides"],
        benefits: ["Long-lasting", "Non-comedogenic", "SPF 15", "Hydrating"],
        howToUse: "Apply with fingers or brush in circular motions, starting from the center of the face",
        shelfLife: "24 months",
        isNew: true
    },
    {
        id: 2,
        name: "Matte Lipstick",
        category: "lipstick",
        price: "$19.99",
        image: "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        description: "Rich, matte finish lipstick with intense color payoff and comfortable wear",
        rating: 4.8,
        reviews: 256,
        skinTypes: ["All"],
        coverage: "Full",
        finish: "Matte",
        brand: "SkinGenie",
        size: "3.5g",
        ingredients: ["Castor Oil", "Beeswax", "Vitamin E", "Color Pigments"],
        benefits: ["Long-lasting", "Transfer-resistant", "Moisturizing", "Rich color"],
        howToUse: "Apply directly to lips or use a lip brush for precise application",
        shelfLife: "18 months",
        discount: 15
    },
    {
        id: 3,
        name: "Eyeshadow Palette",
        category: "eyeshadow",
        price: "$39.99",
        image: "https://images.unsplash.com/photo-1586495777744-4413f21062fa?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        description: "12-color eyeshadow palette with matte and shimmer finishes",
        rating: 4.6,
        reviews: 189,
        skinTypes: ["All"],
        coverage: "Buildable",
        finish: "Multiple",
        brand: "SkinGenie",
        size: "15g",
        ingredients: ["Talc", "Mica", "Iron Oxides", "Titanium Dioxide"],
        benefits: ["Highly pigmented", "Blendable", "Long-lasting", "Versatile"],
        howToUse: "Apply with eyeshadow brush, blend colors for desired look",
        shelfLife: "24 months",
        isNew: true
    }
];

// Product Card Creation
function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card fade-in';
    card.dataset.id = product.id;
    
    const badge = product.isNew ? 'New' : product.discount ? `${product.discount}% OFF` : null;
    
    card.innerHTML = `
        <div class="image-container">
            ${badge ? `<div class="badge">${badge}</div>` : ''}
            <img src="${product.image}" alt="${product.name}">
        </div>
        <div class="product-info">
            <h3>${product.name}</h3>
            <div class="rating">
                ${createStarRating(product.rating)}
                <span>(${product.reviews} reviews)</span>
            </div>
            <p class="description">${product.description}</p>
            <div class="product-details">
                <span>${product.skinTypes.join(', ')}</span>
                <span>${product.coverage}</span>
                <span>${product.finish}</span>
            </div>
            <div class="price-container">
                <div class="price">${product.price}</div>
                <div class="product-actions">
                    <button class="btn-primary add-to-cart" data-id="${product.id}">
                        <i class="fas fa-shopping-cart"></i>
                        Add to Cart
                    </button>
                    <button class="btn-secondary add-to-wishlist" data-id="${product.id}">
                        <i class="fas fa-heart"></i>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add event listeners
    const addToCartBtn = card.querySelector('.add-to-cart');
    const addToWishlistBtn = card.querySelector('.add-to-wishlist');
    
    // Make the entire card clickable except for the action buttons
    card.addEventListener('click', (e) => {
        // Don't trigger if clicking on action buttons
        if (e.target.closest('.product-actions')) return;
        showProductDetails(product.id);
    });
    
    addToCartBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent card click event
        addToCart(product);
        addToCartBtn.innerHTML = '<i class="fas fa-check"></i> Added!';
        setTimeout(() => {
            addToCartBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
        }, 2000);
    });
    
    addToWishlistBtn.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent card click event
        addToWishlist(product);
        addToWishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
        addToWishlistBtn.style.color = 'var(--primary-color)';
        setTimeout(() => {
            addToWishlistBtn.style.color = '';
        }, 2000);
    });
    
    return card;
}

// Star Rating Helper
function createStarRating(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let stars = '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (hasHalfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    
    return stars;
}

// Product Display
function displayProducts(category = 'all') {
    const productGrid = document.querySelector('.product-grid');
    if (!productGrid) return;

    productGrid.innerHTML = '';
    const filteredProducts = category === 'all' 
        ? products 
        : products.filter(product => product.category === category);

    filteredProducts.forEach((product, index) => {
        const card = createProductCard(product);
        card.style.animationDelay = `${index * 0.1}s`;
        productGrid.appendChild(card);
    });
}

// Quick View Modal
function showQuickView(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <div class="quick-view-content">
                <div class="quick-view-image">
                    <img src="${product.image}" alt="${product.name}">
                </div>
                <div class="quick-view-info">
                    <h3>${product.name}</h3>
                    <div class="rating">
                        ${createStarRating(product.rating)}
                        <span>(${product.reviews} reviews)</span>
                    </div>
                    <p class="price">${product.price}</p>
                    <p class="description">${product.description}</p>
                    <div class="product-actions">
                        <button class="btn-primary add-to-cart">
                            <i class="fas fa-shopping-cart"></i>
                            Add to Cart
                        </button>
                        <button class="btn-secondary add-to-wishlist">
                            <i class="fas fa-heart"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    const addToCartBtn = modal.querySelector('.add-to-cart');
    const addToWishlistBtn = modal.querySelector('.add-to-wishlist');
    
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    addToCartBtn.addEventListener('click', () => {
        addToCart(product);
        addToCartBtn.innerHTML = '<i class="fas fa-check"></i> Added!';
        setTimeout(() => {
            addToCartBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
        }, 2000);
    });
    
    addToWishlistBtn.addEventListener('click', () => {
        addToWishlist(product);
        addToWishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
        addToWishlistBtn.style.color = 'var(--primary-color)';
        setTimeout(() => {
            addToWishlistBtn.style.color = '';
        }, 2000);
    });
}

// Product Details Modal
function showProductDetails(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <div class="product-details-content">
                <div class="product-details-image">
                    <img src="${product.image}" alt="${product.name}">
                    ${product.isNew ? '<div class="badge">New</div>' : ''}
                    ${product.discount ? `<div class="badge discount">${product.discount}% OFF</div>` : ''}
                </div>
                <div class="product-details-info">
                    <h3>${product.name}</h3>
                    <div class="rating">
                        ${createStarRating(product.rating)}
                        <span>(${product.reviews} reviews)</span>
                    </div>
                    <p class="price">${product.price}</p>
                    <p class="description">${product.description}</p>
                    
                    <div class="product-specs">
                        <h4>Product Specifications</h4>
                        <ul>
                            <li><strong>Brand:</strong> ${product.brand}</li>
                            <li><strong>Size:</strong> ${product.size}</li>
                            <li><strong>Skin Types:</strong> ${product.skinTypes.join(', ')}</li>
                            <li><strong>Coverage:</strong> ${product.coverage}</li>
                            <li><strong>Finish:</strong> ${product.finish}</li>
                            <li><strong>Shelf Life:</strong> ${product.shelfLife}</li>
                        </ul>
                    </div>

                    <div class="product-ingredients">
                        <h4>Key Ingredients</h4>
                        <ul>
                            ${product.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="product-benefits">
                        <h4>Benefits</h4>
                        <ul>
                            ${product.benefits.map(benefit => `<li>${benefit}</li>`).join('')}
                        </ul>
                    </div>

                    <div class="product-usage">
                        <h4>How to Use</h4>
                        <p>${product.howToUse}</p>
                    </div>

                    <div class="product-actions">
                        <button class="btn-primary add-to-cart">
                            <i class="fas fa-shopping-cart"></i>
                            Add to Cart
                        </button>
                        <button class="btn-secondary add-to-wishlist">
                            <i class="fas fa-heart"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add event listeners
    const closeBtn = modal.querySelector('.close-modal');
    const addToCartBtn = modal.querySelector('.add-to-cart');
    const addToWishlistBtn = modal.querySelector('.add-to-wishlist');
    
    closeBtn.addEventListener('click', () => {
        modal.remove();
    });
    
    addToCartBtn.addEventListener('click', () => {
        addToCart(product);
        addToCartBtn.innerHTML = '<i class="fas fa-check"></i> Added!';
        setTimeout(() => {
            addToCartBtn.innerHTML = '<i class="fas fa-shopping-cart"></i> Add to Cart';
        }, 2000);
    });
    
    addToWishlistBtn.addEventListener('click', () => {
        addToWishlist(product);
        addToWishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
        addToWishlistBtn.style.color = 'var(--primary-color)';
        setTimeout(() => {
            addToWishlistBtn.style.color = '';
        }, 2000);
    });
}

// Initialize product display
document.addEventListener('DOMContentLoaded', () => {
    displayProducts();
    
    // Add filter button event listeners
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const productGrid = document.querySelector('.product-grid');
            productGrid.style.opacity = '0';
            setTimeout(() => {
                displayProducts(button.dataset.filter);
                productGrid.style.opacity = '1';
            }, 300);
        });
    });
}); 