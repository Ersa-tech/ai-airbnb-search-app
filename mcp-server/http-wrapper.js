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

// Mock Airbnb search endpoint (simplified for internal use)
app.post('/search', async (req, res) => {
    try {
        const { location, checkin, checkout, adults, children, infants, pets, minPrice, maxPrice } = req.body;
        
        console.log('Search request:', req.body);
        
        // Mock property data for development (replace with actual MCP server integration)
        const mockProperties = [
            {
                id: '12345',
                title: 'Beautiful Beach House in ' + (location || 'California'),
                location: location || 'Malibu, CA',
                price: Math.floor(Math.random() * 300) + 100,
                rating: (Math.random() * 2 + 3).toFixed(1),
                images: ['https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800'],
                amenities: ['WiFi', 'Pool', 'Kitchen', 'Parking'],
                guests: adults || 2,
                bedrooms: Math.floor(Math.random() * 4) + 1,
                bathrooms: Math.floor(Math.random() * 3) + 1
            },
            {
                id: '12346',
                title: 'Modern Downtown Apartment in ' + (location || 'California'),
                location: location || 'San Francisco, CA',
                price: Math.floor(Math.random() * 250) + 150,
                rating: (Math.random() * 2 + 3).toFixed(1),
                images: ['https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800'],
                amenities: ['WiFi', 'Gym', 'Kitchen', 'City View'],
                guests: adults || 2,
                bedrooms: Math.floor(Math.random() * 3) + 1,
                bathrooms: Math.floor(Math.random() * 2) + 1
            },
            {
                id: '12347',
                title: 'Cozy Mountain Cabin in ' + (location || 'California'),
                location: location || 'Lake Tahoe, CA',
                price: Math.floor(Math.random() * 200) + 80,
                rating: (Math.random() * 2 + 3).toFixed(1),
                images: ['https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800'],
                amenities: ['WiFi', 'Fireplace', 'Kitchen', 'Mountain View'],
                guests: adults || 2,
                bedrooms: Math.floor(Math.random() * 3) + 2,
                bathrooms: Math.floor(Math.random() * 2) + 1
            },
            {
                id: '12348',
                title: 'Luxury Villa with Pool in ' + (location || 'California'),
                location: location || 'Beverly Hills, CA',
                price: Math.floor(Math.random() * 500) + 300,
                rating: (Math.random() * 1 + 4).toFixed(1),
                images: ['https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800'],
                amenities: ['WiFi', 'Pool', 'Spa', 'Garden', 'Parking'],
                guests: adults || 2,
                bedrooms: Math.floor(Math.random() * 4) + 3,
                bathrooms: Math.floor(Math.random() * 3) + 2
            },
            {
                id: '12349',
                title: 'Charming Studio in ' + (location || 'California'),
                location: location || 'Santa Monica, CA',
                price: Math.floor(Math.random() * 150) + 75,
                rating: (Math.random() * 2 + 3).toFixed(1),
                images: ['https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'],
                amenities: ['WiFi', 'Kitchen', 'Beach Access'],
                guests: adults || 2,
                bedrooms: 1,
                bathrooms: 1
            }
        ];

        // Filter by price if specified
        let filteredProperties = mockProperties;
        if (minPrice) {
            filteredProperties = filteredProperties.filter(p => p.price >= minPrice);
        }
        if (maxPrice) {
            filteredProperties = filteredProperties.filter(p => p.price <= maxPrice);
        }

        // Return exactly 5 properties for the carousel
        const properties = filteredProperties.slice(0, 5);

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

        console.log(`Returning ${properties.length} properties`);
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
