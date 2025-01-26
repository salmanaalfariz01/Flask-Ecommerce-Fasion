-- fasion.`order` definition
CREATE TABLE `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(20) NOT NULL,
    gender ENUM('men', 'women', 'child') NOT NULL,
    size ENUM('S', 'M', 'L', 'XL', 'XXL') NOT NULL,
    color VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    price INT NOT NULL,
    status ENUM('Pending', 'Paid', 'Shipped', 'Delivered', 'Cancelled') NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Tanggal pesanan (gunakan default untuk waktu saat ini)

    customer_link INT NOT NULL,
    product_link INT NOT NULL,

    -- Menambahkan Foreign Keys
    FOREIGN KEY (customer_link) REFERENCES customer(id) ON DELETE CASCADE,
    FOREIGN KEY (product_link) REFERENCES product(id) ON DELETE CASCADE
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


-- fasion.payment definition

CREATE TABLE `payment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name_platform` varchar(100) NOT NULL,
  `number` varchar(20) NOT NULL,
  `picture` varchar(100) NOT NULL,
  `date_joined` datetime DEFAULT current_timestamp(),
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name_platform`),
  UNIQUE KEY `number` (`number`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;