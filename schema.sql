-- Create the amazon_products table
CREATE TABLE amazon_products (
    -- Primary key and basic product info
    product_id VARCHAR(20) PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    
    -- Price information
    discounted_price DECIMAL(10, 2),  -- Converting from ₹ string to decimal
    actual_price DECIMAL(10, 2),      -- Converting from ₹ string to decimal
    discount_percentage INTEGER,       -- Converting from percentage string to integer
    
    -- Rating information
    rating DECIMAL(2, 1),             -- Already in correct format
    rating_count INTEGER,             -- Converting from string with commas to integer
    
    -- Product details
    about_product TEXT,
    
    -- URLs
    img_link TEXT,
    product_link TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the product_reviews table
CREATE TABLE product_reviews (
    -- Primary key and foreign key
    review_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES amazon_products(product_id),
    
    -- User information
    user_id VARCHAR(50),
    user_name TEXT,
    
    -- Review content
    review_title TEXT,
    review_content TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_products_category ON amazon_products(category);
CREATE INDEX idx_products_rating ON amazon_products(rating);
CREATE INDEX idx_reviews_product_id ON product_reviews(product_id);
CREATE INDEX idx_reviews_user_id ON product_reviews(user_id);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_amazon_products_updated_at
    BEFORE UPDATE ON amazon_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_product_reviews_updated_at
    BEFORE UPDATE ON product_reviews
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments to explain the tables and important columns
COMMENT ON TABLE amazon_products IS 'Main table storing Amazon product information';
COMMENT ON TABLE product_reviews IS 'Table storing user reviews for products';
COMMENT ON COLUMN amazon_products.discounted_price IS 'Current price in rupees (₹)';
COMMENT ON COLUMN amazon_products.actual_price IS 'Original price in rupees (₹)';
COMMENT ON COLUMN amazon_products.rating IS 'Product rating from 1 to 5';
COMMENT ON COLUMN amazon_products.rating_count IS 'Number of ratings received'; 