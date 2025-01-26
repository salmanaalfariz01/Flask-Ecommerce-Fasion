-- fasion.`order` definition
CREATE TABLE `order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` varchar(20) NOT NULL,
  `gender` enum('men','women','child') NOT NULL,
  `size` enum('S','M','L','XL') NOT NULL,
  `color` varchar(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `price` INT NOT NULL,
  `status` ENUM('Processing', 'Completed', 'Failed') DEFAULT 'Processing' NOT NULL,
  `payment_id` INT NOT NULL,
  `customer_link` int(11) NOT NULL,
  `product_link` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_link` (`customer_link`),
  KEY `payment_id` (`payment_id`),
  KEY `product_link` (`product_link`),
  CONSTRAINT `order_ibfk_1` FOREIGN KEY (`customer_link`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_ibfk_2` FOREIGN KEY (`payment_id`) REFERENCES `payment` (`id`) ON DELETE CASCADE,
  CONSTRAINT `order_ibfk_3` FOREIGN KEY (`product_link`) REFERENCES `product` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;




CREATE TABLE payment (
  id INT PRIMARY KEY,
  customer_link INT NOT NULL,
  total_amount INT NOT NULL,
  payment_status ENUM('Pending', 'Paid', 'Failed') DEFAULT 'Pending' NOT NULL, -- Pending, Paid, Failed
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_link) REFERENCES Customer(id)
);

-- fasion.cart definition

CREATE TABLE `cart` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category` varchar(20) NOT NULL,
  `gender` enum('men','women','child') NOT NULL,
  `size` enum('S','M','L','XL') NOT NULL,
  `color` varchar(20) NOT NULL,
  `quantity` int(11) NOT NULL,
  `customer_link` int(11) NOT NULL,
  `product_link` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `customer_link` (`customer_link`),
  KEY `product_link` (`product_link`),
  CONSTRAINT `cart_ibfk_1` FOREIGN KEY (`customer_link`) REFERENCES `customer` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cart_ibfk_2` FOREIGN KEY (`product_link`) REFERENCES `product` (`id`) ON DELETE CASCADE
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
  `username` varchar(100) DEFAULT NULL,
  `password_hash` varchar(150) DEFAULT NULL,
  `date_joined` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;