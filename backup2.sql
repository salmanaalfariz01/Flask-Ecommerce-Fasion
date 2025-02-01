-- fasion.`order` definition
CREATE TABLE `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `product_name` varchar(100) NOT NULL,
    `product_picture` varchar(1000) NOT NULL,
    category VARCHAR(20) NOT NULL,
    gender ENUM('men', 'women', 'child') NOT NULL,
    size ENUM('S', 'M', 'L', 'XL', 'XXL') NOT NULL,
    color VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    price INT NOT NULL,
    status ENUM('Pending', 'Paid', 'On Delivery', 'The order has arrived') NOT NULL,
    shipping_cost INT NOT NULL,               # Total jumlah produk
    grand_total INT NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Tanggal pesanan (gunakan default untuk waktu saat ini)

    customer_id INT NOT NULL,
    product_id INT NOT NULL,

    -- Menambahkan Foreign Keys
    FOREIGN KEY (customer_id) REFERENCES customer(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
);


-- fasion.cart definition

CREATE TABLE `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) NOT NULL,
  `category` varchar(20) NOT NULL,
  `gender` enum('men','women','child') NOT NULL,
  `size` enum('S','M','L','XL') NOT NULL,
  `color` varchar(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `customer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- fasion.product definition

CREATE TABLE `product` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_name` varchar(100) NOT NULL,
  `current_price` int(11) NOT NULL,
  `previous_price` int(11) NOT NULL,
  `size` enum('S','M','L','XL') NOT NULL,
  `category` varchar(20) NOT NULL,
  `gender` enum('men','women','child') NOT NULL,
  `color` varchar(20) NOT NULL,
  `in_stock` int(11) NOT NULL,
  `product_picture` varchar(1000) NOT NULL,
  `flash_sale` tinyint(1) DEFAULT 0,
  `date_added` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=88 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- fasion.customer definition

CREATE TABLE `customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password_hash` text NOT NULL,
  `address` TEXT NOT NULL,
  `date_joined` datetime DEFAULT current_timestamp(),
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE `payment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `payment_method` varchar(100) NOT NULL,
  `payment_number` varchar(20) NOT NULL,
  `picture` varchar(100) NOT NULL,
  `date_joined` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`payment_method`),
  UNIQUE KEY `number` (`payment_number`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;




-- fasion.`order` definition

CREATE TABLE `order_user` (
  `id` int(11) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `product_picture` varchar(1000) NOT NULL,
  `category` varchar(20) NOT NULL,
  `gender` enum('men','women','child') NOT NULL,
  `size` enum('S','M','L','XL','XXL') NOT NULL,
  `color` varchar(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `status` enum('Pending','Paid','On Delivery','The order has arrived') NOT NULL,
  `shipping_cost` int(11) NOT NULL,
  `grand_total` int(11) NOT NULL,
  `order_date` datetime DEFAULT current_timestamp(),
  `customer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_id` (`customer_id`),
  KEY `product_id` (`product_id`),
  CONSTRAINT `order_user_1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_user_2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

-- fasion.history definition

CREATE TABLE `history` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `customer_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `product_name` varchar(100) NOT NULL,
  `product_picture` varchar(1000) NOT NULL,
  `category` varchar(50) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `size` varchar(10) DEFAULT NULL,
  `color` varchar(20) DEFAULT NULL,
  `quantity` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `shipping_cost` int(11) NOT NULL,
  `grand_total` int(11) NOT NULL,
  `status` varchar(50) NOT NULL,
  `date_completed` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `history_fk1` (`customer_id`),
  KEY `history_fk2` (`product_id`),
  CONSTRAINT `history_fk1` FOREIGN KEY (`customer_id`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  CONSTRAINT `history_fk2` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


-- fasion.payment_status definition

CREATE TABLE `payment_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `status` varchar(50) NOT NULL,
  `payment_file_path` varchar(255) DEFAULT NULL,
  `product_name` varchar(100) NOT NULL,
  `product_picture` varchar(1000) NOT NULL,
  `product_category` varchar(50) NOT NULL,
  `gender` varchar(10) NOT NULL,
  `size` varchar(10) NOT NULL,
  `color` varchar(50) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` int(11) NOT NULL,
  `shipping_cost` int(11) NOT NULL,
  `total` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `order_id` (`order_id`),
  CONSTRAINT `payment_status_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `order` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;