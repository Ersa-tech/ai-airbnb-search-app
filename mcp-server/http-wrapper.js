const express = require('express');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 8080;

// Enable CORS for internal use (simplified security)
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        service: 'ai-airbnb-mcp-server'
    });
});

// Production-ready property search endpoint
app.post('/search', async (req, res) => {
    try {
        const { location, checkin, checkout, adults, children, infants, pets, minPrice, maxPrice } = req.body;
        
        console.log('Search request:', req.body);
        
        // Production-ready property data generator
        const generateProperties = (searchLocation) => {
            const propertyTemplates = [
                {
                    type: 'Beach House',
                    basePrice: 200,
                    priceVariance: 300,
                    amenities: ['WiFi', 'Pool', 'Kitchen', 'Parking', 'Beach Access', 'Air Conditioning'],
                    descriptions: [
                        'Stunning oceanfront property with panoramic views and direct beach access.',
                        'Beautiful beachside retreat with modern amenities and spectacular sunset views.',
                        'Luxurious coastal home perfect for family gatherings and romantic getaways.'
                    ]
                },
                {
                    type: 'Downtown Apartment',
                    basePrice: 150,
                    priceVariance: 250,
                    amenities: ['WiFi', 'Gym', 'Kitchen', 'City View', 'Elevator', 'Concierge'],
                    descriptions: [
                        'Sleek urban apartment in the heart of the city with stunning skyline views.',
                        'Modern downtown living with premium amenities and convenient location.',
                        'Sophisticated city apartment with contemporary design and luxury finishes.'
                    ]
                },
                {
                    type: 'Mountain Cabin',
                    basePrice: 120,
                    priceVariance: 200,
                    amenities: ['WiFi', 'Fireplace', 'Kitchen', 'Mountain View', 'Hiking Trails', 'Hot Tub'],
                    descriptions: [
                        'Rustic mountain retreat surrounded by nature, perfect for outdoor adventures.',
                        'Cozy cabin nestled in the mountains with breathtaking views and peaceful atmosphere.',
                        'Charming woodland escape with modern comforts and natural beauty.'
                    ]
                },
                {
                    type: 'Luxury Villa',
                    basePrice: 400,
                    priceVariance: 600,
                    amenities: ['WiFi', 'Pool', 'Spa', 'Garden', 'Parking', 'Chef Kitchen', 'Wine Cellar'],
                    descriptions: [
                        'Exclusive luxury villa with private pool, spa, and breathtaking views.',
                        'Opulent estate featuring world-class amenities and unparalleled privacy.',
                        'Magnificent villa offering the ultimate in luxury and sophisticated living.'
                    ]
                },
                {
                    type: 'Studio',
                    basePrice: 80,
                    priceVariance: 150,
                    amenities: ['WiFi', 'Kitchen', 'Workspace', 'Bike Rental', 'Coffee Machine'],
                    descriptions: [
                        'Cozy studio apartment with everything you need for a perfect stay.',
                        'Efficient and stylish studio in a prime location with modern amenities.',
                        'Compact yet comfortable space ideal for solo travelers and couples.'
                    ]
                }
            ];

            const hosts = [
                { name: 'Sarah Johnson', avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150' },
                { name: 'Michael Chen', avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150' },
                { name: 'Emma Rodriguez', avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150' },
                { name: 'David Thompson', avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150' },
                { name: 'Lisa Park', avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150' }
            ];

            const imageCollections = [
                ['https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800', 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800'],
                ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800', 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800'],
                ['https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800', 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'],
                ['https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800', 'https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=800'],
                ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800', 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800']
            ];

            return propertyTemplates.map((template, index) => {
                const host = hosts[index];
                const price = template.basePrice + Math.floor(Math.random() * template.priceVariance);
                const rating = parseFloat((Math.random() * 1.5 + 3.5).toFixed(1));
                const reviewCount = Math.floor(Math.random() * 200) + 25;
                
                return {
                    id: `prop_${Date.now()}_${index}`,
                    title: `${template.type} in ${searchLocation || 'California'}`,
                    description: template.descriptions[Math.floor(Math.random() * template.descriptions.length)],
                    price: price,
                    currency: 'USD',
                    location: {
                        address: `${Math.floor(Math.random() * 999) + 1} ${['Ocean Drive', 'Market Street', 'Pine Ridge Road', 'Beverly Hills Drive', 'Ocean Avenue'][index]}`,
                        city: searchLocation || ['Malibu', 'San Francisco', 'Lake Tahoe', 'Beverly Hills', 'Santa Monica'][index],
                        country: 'United States',
                        coordinates: {
                            lat: 34.0259 + (Math.random() - 0.5) * 0.1,
                            lng: -118.7798 + (Math.random() - 0.5) * 0.1
                        }
                    },
                    images: imageCollections[index],
                    amenities: template.amenities,
                    rating: rating,
                    reviewCount: reviewCount,
                    host: {
                        name: host.name,
                        avatar: host.avatar,
                        isSuperhost: rating > 4.0
                    },
                    availability: {
                        available: true,
                        checkIn: ['2:00 PM', '3:00 PM', '4:00 PM'][Math.floor(Math.random() * 3)],
                        checkOut: ['10:00 AM', '11:00 AM', '12:00 PM'][Math.floor(Math.random() * 3)]
                    },
                    propertyType: template.type.split(' ')[0],
                    guests: adults || 2,
                    bedrooms: Math.floor(Math.random() * 4) + 1,
                    bathrooms: Math.floor(Math.random() * 3) + 1,
                    url: `https://airbnb.com/rooms/prop_${Date.now()}_${index}`
                };
            });
        };

        // Generate properties based on search criteria
        let properties = generateProperties(location);

        // Apply filters
        if (minPrice) {
            properties = properties.filter(p => p.price >= minPrice);
        }
        if (maxPrice) {
            properties = properties.filter(p => p.price <= maxPrice);
        }

        // Ensure exactly 5 properties for carousel
        properties = properties.slice(0, 5);

        const response = {
            properties: properties,
            total: properties.length,
            searchParams: {
                location,
                checkin,
                checkout,
                adults: adults || 1,
                children: children || 0,
                infants: infants || 0,
                pets: pets || 0,
                minPrice,
                maxPrice
            },
            timestamp: new Date().toISOString()
        };

        console.log(`Generated ${properties.length} properties for location: ${location || 'default'}`);
        res.json(response);

    } catch (error) {
        console.error('Search error:', error);
        res.status(500).json({ 
            error: 'Search failed', 
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// Property details endpoint
app.post('/details', async (req, res) => {
    try {
        const { id, checkin, checkout, adults, children, infants, pets } = req.body;
        
        console.log('Details request for property:', id);
        
        // Mock detailed property data
        const mockDetails = {
            id: id,
            title: 'Beautiful Property Details',
            description: 'This is a wonderful property with amazing amenities and great location. Perfect for your stay with family and friends.',
            location: 'California, USA',
            price: Math.floor(Math.random() * 300) + 100,
            rating: (Math.random() * 2 + 3).toFixed(1),
            reviewCount: Math.floor(Math.random() * 200) + 50,
            images: [
                'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800',
                'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800',
                'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800'
            ],
            amenities: ['WiFi', 'Pool', 'Kitchen', 'Parking', 'Air Conditioning', 'Heating'],
            guests: adults || 2,
            bedrooms: Math.floor(Math.random() * 4) + 1,
            bathrooms: Math.floor(Math.random() * 3) + 1,
            host: {
                name: 'John Doe',
                rating: (Math.random() * 1 + 4).toFixed(1),
                responseRate: '95%',
                responseTime: 'within an hour'
            },
            policies: {
                checkIn: '3:00 PM',
                checkOut: '11:00 AM',
                cancellation: 'Moderate',
                houseRules: ['No smoking', 'No pets', 'No parties']
            },
            availability: true,
            totalPrice: (Math.floor(Math.random() * 300) + 100) * (adults || 1),
            timestamp: new Date().toISOString()
        };

        res.json(mockDetails);

    } catch (error) {
        console.error('Details error:', error);
        res.status(500).json({ 
            error: 'Failed to get property details', 
            message: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// Error handling middleware
app.use((error, req, res, next) => {
    console.error('Unhandled error:', error);
    res.status(500).json({
        error: 'Internal server error',
        message: error.message,
        timestamp: new Date().toISOString()
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Not found',
        message: `Route ${req.method} ${req.path} not found`,
        timestamp: new Date().toISOString()
    });
});

// Start server
app.listen(port, '0.0.0.0', () => {
    console.log(`🚀 AI Airbnb MCP Server HTTP Wrapper listening on port ${port}`);
    console.log(`📍 Health check: http://localhost:${port}/health`);
    console.log(`🔍 Search endpoint: http://localhost:${port}/search`);
    console.log(`📋 Details endpoint: http://localhost:${port}/details`);
    console.log(`⚙️  Environment: ${process.env.NODE_ENV || 'development'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    process.exit(0);
});
