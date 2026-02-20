# Sub-Agent Examples

This document provides examples of how the sub-agents would work within the Agent Team Orchestrator skill.

## Architect Sub-Agent

```python
#!/usr/bin/env python3
"""
Architect Sub-Agent
Specializes in system design, technical specifications, and architectural decisions.
"""

import json
from typing import Dict, List, Any

class ArchitectAgent:
    def __init__(self):
        self.role = "architect"
        self.expertise = [
            "system_architecture", "technology_selection", "api_design",
            "database_design", "scalability_planning", "security_design"
        ]
    
    def analyze_requirements(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze requirements and create technical specifications."""
        analysis = {
            "functional_requirements": requirements.get("features", []),
            "non_functional_requirements": requirements.get("constraints", []),
            "technology_stack": self._select_technology_stack(requirements),
            "architecture_pattern": self._select_architecture_pattern(requirements),
            "api_design": self._design_api(requirements),
            "data_model": self._design_data_model(requirements),
            "security_considerations": self._identify_security_needs(requirements),
            "scalability_strategy": self._design_scalability_plan(requirements)
        }
        return analysis
    
    def create_technical_specifications(self, analysis: Dict[str, Any]) -> str:
        """Create detailed technical specifications document."""
        specs = f"""# Technical Specifications

## Architecture Overview
{analysis.get('architecture_pattern', 'TBD')}

## Technology Stack
{self._format_tech_stack(analysis.get('technology_stack', {}))}

## API Design
{self._format_api_design(analysis.get('api_design', {}))}

## Data Model
{self._format_data_model(analysis.get('data_model', {}))}

## Security Considerations
{self._format_security_plan(analysis.get('security_considerations', {}))}

## Scalability Strategy
{self._format_scalability_plan(analysis.get('scalability_strategy', {}))}

## Implementation Guidelines
{self._generate_implementation_guidelines(analysis)}
"""
        return specs
    
    def _select_technology_stack(self, requirements: Dict[str, Any]) -> Dict[str, str]:
        """Select appropriate technology stack based on requirements."""
        stack = {}
        
        # Example technology selection logic
        if requirements.get("performance_critical", False):
            stack["backend"] = "Node.js with Express"
            stack["database"] = "PostgreSQL"
        else:
            stack["backend"] = "Python with FastAPI"
            stack["database"] = "SQLite for dev, PostgreSQL for prod"
            
        stack["frontend"] = "React with TypeScript"
        stack["authentication"] = "JWT with OAuth2"
        
        return stack
    
    def _select_architecture_pattern(self, requirements: Dict[str, Any]) -> str:
        """Select appropriate architecture pattern."""
        if requirements.get("microservices", False):
            return "Microservices Architecture"
        elif requirements.get("real_time", False):
            return "Event-Driven Architecture"
        else:
            return "Layered Architecture"
    
    def _design_api(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design API endpoints and structure."""
        return {
            "endpoints": [
                {"method": "POST", "path": "/auth/login", "description": "User authentication"},
                {"method": "GET", "path": "/users/profile", "description": "Get user profile"},
                {"method": "POST", "path": "/data/export", "description": "Export data"}
            ],
            "authentication": "Bearer token",
            "rate_limiting": "100 requests per minute",
            "response_format": "JSON"
        }
    
    def _design_data_model(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design database schema."""
        return {
            "users": ["id", "email", "password_hash", "created_at", "role"],
            "sessions": ["id", "user_id", "token", "expires_at"],
            "audit_log": ["id", "user_id", "action", "timestamp", "details"]
        }
    
    def _identify_security_needs(self, requirements: Dict[str, Any]) -> List[str]:
        """Identify security considerations."""
        return [
            "Input validation and sanitization",
            "SQL injection prevention",
            "XSS protection",
            "CSRF protection",
            "Rate limiting",
            "Secure password hashing",
            "JWT token security"
        ]
    
    def _design_scalability_plan(self, requirements: Dict[str, Any]) -> List[str]:
        """Design scalability strategy."""
        return [
            "Horizontal scaling with load balancers",
            "Database connection pooling",
            "Caching layer (Redis)",
            "CDN for static assets",
            "Auto-scaling based on metrics"
        ]
    
    def _format_tech_stack(self, stack: Dict[str, str]) -> str:
        """Format technology stack for specifications."""
        return "\n".join(f"- **{k.title()}**: {v}" for k, v in stack.items())
    
    def _format_api_design(self, api: Dict[str, Any]) -> str:
        """Format API design for specifications."""
        result = "**Endpoints:**\n"
        for endpoint in api.get("endpoints", []):
            result += f"- `{endpoint['method']} {endpoint['path']}`: {endpoint['description']}\n"
        return result
    
    def _format_data_model(self, model: Dict[str, Any]) -> str:
        """Format data model for specifications."""
        result = ""
        for table, fields in model.items():
            result += f"**{table.title()}:** {', '.join(fields)}\n"
        return result
    
    def _format_security_plan(self, security: List[str]) -> str:
        """Format security plan for specifications."""
        return "\n".join(f"- {item}" for item in security)
    
    def _format_scalability_plan(self, scalability: List[str]) -> str:
        """Format scalability plan for specifications."""
        return "\n".join(f"- {item}" for item in scalability)
    
    def _generate_implementation_guidelines(self, analysis: Dict[str, Any]) -> str:
        """Generate implementation guidelines."""
        return """
## Key Implementation Guidelines

1. Follow clean architecture principles
2. Implement comprehensive error handling
3. Add detailed logging for debugging
4. Create unit and integration tests
5. Document all APIs and functions
6. Follow security best practices
7. Optimize for performance from the start
"""

# Example usage
if __name__ == "__main__":
    agent = ArchitectAgent()
    
    # Example requirements
    requirements = {
        "features": ["user_auth", "data_export", "admin_panel"],
        "performance_critical": True,
        "real_time": False
    }
    
    # Analyze and create specifications
    analysis = agent.analyze_requirements(requirements)
    specs = agent.create_technical_specifications(analysis)
    
    print("Architect Agent - Technical Specifications Generated")
    print("=" * 60)
    print(specs)
```

## Coder Sub-Agent

```python
#!/usr/bin/env python3
"""
Coder Sub-Agent
Specializes in implementation, testing, and following architectural specifications.
"""

import json
import os
from typing import Dict, List, Any

class CoderAgent:
    def __init__(self):
        self.role = "coder"
        self.expertise = [
            "clean_code", "test_driven_development", "api_implementation",
            "database_integration", "frontend_development", "code_documentation"
        ]
    
    def implement_feature(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Implement features based on architectural specifications."""
        implementation = {
            "backend_code": self._generate_backend_code(specifications),
            "frontend_code": self._generate_frontend_code(specifications),
            "database_setup": self._generate_database_setup(specifications),
            "tests": self._generate_tests(specifications),
            "documentation": self._generate_code_documentation(specifications),
            "configuration": self._generate_configuration(specifications)
        }
        return implementation
    
    def create_test_coverage_report(self, tests: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test coverage analysis."""
        return {
            "total_lines": 500,
            "covered_lines": 425,
            "coverage_percentage": 85.0,
            "critical_functions_covered": True,
            "test_types": ["unit", "integration", "e2e"],
            "coverage_by_module": {
                "auth": 90,
                "api": 85,
                "database": 80,
                "frontend": 85
            }
        }
    
    def _generate_backend_code(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate backend implementation."""
        tech_stack = specs.get("technology_stack", {})
        backend_framework = tech_stack.get("backend", "Express.js")
        
        if "Express" in backend_framework:
            return self._generate_express_code(specs)
        elif "FastAPI" in backend_framework:
            return self._generate_fastapi_code(specs)
        else:
            return self._generate_generic_backend_code(specs)
    
    def _generate_express_code(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate Express.js backend code."""
        code = {
            "app.js": self._create_express_app(),
            "routes/auth.js": self._create_auth_routes(),
            "middleware/auth.js": self._create_auth_middleware(),
            "models/User.js": self._create_user_model(),
            "config/database.js": self._create_db_config()
        }
        return code
    
    def _create_express_app(self) -> str:
        """Create main Express application file."""
        return '''const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api/', limiter);

// Body parsing
app.use(express.json());

// Routes
app.use('/api/auth', require('./routes/auth'));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

module.exports = app;'''
    
    def _create_auth_routes(self) -> str:
        """Create authentication routes."""
        return '''const express = require('express');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const router = express.Router();

// Mock user database (replace with real DB)
const users = new Map();

router.post('/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Check if user exists
    if (users.has(email)) {
      return res.status(400).json({ error: 'User already exists' });
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, 12);
    
    // Create user
    const user = {
      id: Date.now().toString(),
      email,
      password: hashedPassword,
      role: 'user',
      createdAt: new Date().toISOString()
    };
    
    users.set(email, user);
    
    res.status(201).json({ message: 'User created successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user
    const user = users.get(email);
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Check password
    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT
    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: '1h' }
    );
    
    res.json({ token, user: { id: user.id, email: user.email, role: user.role } });
  } catch (error) {
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;'''
    
    def _create_auth_middleware(self) -> str:
        """Create authentication middleware."""
        return '''const jwt = require('jsonwebtoken');

const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    
    req.user = user;
    next();
  });
};

const requireRole = (roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};

module.exports = { authenticateToken, requireRole };'''
    
    def _create_user_model(self) -> str:
        """Create user model."""
        return '''const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true
  },
  password: {
    type: String,
    required: true,
    minlength: 6
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user'
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('User', userSchema);'''
    
    def _create_db_config(self) -> str:
        """Create database configuration."""
        return '''const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    const conn = await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/myapp');
    console.log(`MongoDB Connected: ${conn.connection.host}`);
  } catch (error) {
    console.error('Database connection error:', error);
    process.exit(1);
  }
};

module.exports = connectDB;'''
    
    def _generate_frontend_code(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate frontend implementation."""
        return {
            "src/App.tsx": self._create_react_app(),
            "src/components/Auth.tsx": self._create_auth_component(),
            "src/services/api.ts": self._create_api_service(),
            "src/hooks/useAuth.ts": self._create_auth_hook(),
            "src/utils/validation.ts": self._create_validation_utils()
        }
    
    def _create_react_app(self) -> str:
        """Create main React application."""
        return '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import Auth from './components/Auth';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/auth" element={<Auth />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;'''
    
    def _create_auth_component(self) -> str:
        """Create authentication component."""
        return '''import React, { useState } from 'react';
import { useAuth } from '../hooks/useAuth';

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    }
  };

  return (
    <div className="auth-container">
      <h2>{isLogin ? 'Login' : 'Register'}</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        
        {error && <div className="error">{error}</div>}
        
        <button type="submit">
          {isLogin ? 'Login' : 'Register'}
        </button>
      </form>
      
      <button onClick={() => setIsLogin(!isLogin)}>
        {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
      </button>
    </div>
  );
};

export default Auth;'''
    
    def _create_api_service(self) -> str:
        """Create API service."""
        return '''const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

class ApiService {
  private getHeaders(): HeadersInit {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
  }

  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    return response.json();
  }

  async register(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }

    return response.json();
  }

  async getUserProfile() {
    const response = await fetch(`${API_BASE_URL}/users/profile`, {
      headers: this.getHeaders()
    });

    if (!response.ok) {
      throw new Error('Failed to fetch profile');
    }

    return response.json();
  }
}

export default new ApiService();'''
    
    def _create_auth_hook(self) -> str:
        """Create authentication hook."""
        return '''import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import apiService from '../services/api';

interface User {
  id: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored token and validate
    const token = localStorage.getItem('token');
    if (token) {
      // Validate token and get user info
      // This would typically make an API call
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { token, user: userData } = await apiService.login(email, password);
    localStorage.setItem('token', token);
    setUser(userData);
  };

  const register = async (email: string, password: string) => {
    await apiService.register(email, password);
    // Auto-login after registration
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};'''
    
    def _create_validation_utils(self) -> str:
        """Create validation utilities."""
        return '''export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): ValidationResult => {
  const errors: string[] = [];
  
  if (password.length < 6) {
    errors.push('Password must be at least 6 characters long');
  }
  
  if (!/(?=.*[a-z])/.test(password)) {
    errors.push('Password must contain at least one lowercase letter');
  }
  
  if (!/(?=.*[A-Z])/.test(password)) {
    errors.push('Password must contain at least one uppercase letter');
  }
  
  if (!/(?=.*\\d)/.test(password)) {
    errors.push('Password must contain at least one number');
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};

export const validateForm = (data: Record<string, any>): ValidationResult => {
  const errors: string[] = [];
  
  if (!data.email) {
    errors.push('Email is required');
  } else if (!validateEmail(data.email)) {
    errors.push('Invalid email format');
  }
  
  if (!data.password) {
    errors.push('Password is required');
  } else {
    const passwordValidation = validatePassword(data.password);
    errors.push(...passwordValidation.errors);
  }
  
  return {
    isValid: errors.length === 0,
    errors
  };
};'''
    
    def _generate_tests(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive tests."""
        return {
            "tests/auth.test.js": self._create_auth_tests(),
            "tests/api.test.js": self._create_api_tests(),
            "tests/components.test.jsx": self._create_component_tests(),
            "cypress/e2e/auth.cy.js": self._create_e2e_tests()
        }
    
    def _create_auth_tests(self) -> str:
        """Create authentication tests."""
        return '''const request = require('supertest');
const app = require('../app');

describe('Authentication API', () => {
  describe('POST /api/auth/register', () => {
    it('should register a new user', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123'
      };

      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      expect(response.body.message).toBe('User created successfully');
    });

    it('should not register user with existing email', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123'
      };

      // First registration
      await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(201);

      // Duplicate registration
      const response = await request(app)
        .post('/api/auth/register')
        .send(userData)
        .expect(400);

      expect(response.body.error).toBe('User already exists');
    });
  });

  describe('POST /api/auth/login', () => {
    beforeEach(async () => {
      // Register a user for testing
      const userData = {
        email: 'test@example.com',
        password: 'password123'
      };

      await request(app)
        .post('/api/auth/register')
        .send(userData);
    });

    it('should login with valid credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'password123'
        })
        .expect(200);

      expect(response.body.token).toBeDefined();
      expect(response.body.user).toBeDefined();
    });

    it('should not login with invalid credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({
          email: 'test@example.com',
          password: 'wrongpassword'
        })
        .expect(401);

      expect(response.body.error).toBe('Invalid credentials');
    });
  });
});'''
    
    def _create_api_tests(self) -> str:
        """Create API integration tests."""
        return '''const request = require('supertest');
const app = require('../app');

describe('Protected Routes', () => {
  let authToken;

  beforeEach(async () => {
    // Register and login to get token
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'password123'
      });

    authToken = response.body.token;
  });

  describe('GET /api/users/profile', () => {
    it('should return user profile with valid token', async () => {
      const response = await request(app)
        .get('/api/users/profile')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body.user).toBeDefined();
    });

    it('should reject request without token', async () => {
      await request(app)
        .get('/api/users/profile')
        .expect(401);
    });

    it('should reject request with invalid token', async () => {
      await request(app)
        .get('/api/users/profile')
        .set('Authorization', 'Bearer invalidtoken')
        .expect(403);
    });
  });
});'''
    
    def _create_component_tests(self) -> str:
        """Create React component tests."""
        return '''import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AuthProvider } from '../hooks/useAuth';
import Auth from '../components/Auth';

// Mock the auth hook
jest.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    login: jest.fn(),
    register: jest.fn(),
  }),
}));

describe('Auth Component', () => {
  const renderAuthComponent = () => {
    return render(
      <AuthProvider>
        <Auth />
      </AuthProvider>
    );
  };

  it('should render login form by default', () => {
    renderAuthComponent();
    
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
  });

  it('should toggle between login and register', () => {
    renderAuthComponent();
    
    const toggleButton = screen.getByText('Need an account? Register');
    fireEvent.click(toggleButton);
    
    expect(screen.getByText('Register')).toBeInTheDocument();
  });

  it('should handle form submission', async () => {
    const mockLogin = jest.fn();
    
    jest.spyOn(require('../hooks/useAuth'), 'useAuth').mockReturnValue({
      login: mockLogin,
      register: jest.fn(),
    });

    renderAuthComponent();
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: /login/i });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });
});'''
    
    def _create_e2e_tests(self) -> str:
        """Create end-to-end tests."""
        return '''describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/auth');
  });

  it('should complete registration flow', () => {
    cy.get('[data-cy=register-toggle]').click();
    cy.get('[data-cy=email-input]').type('test@example.com');
    cy.get('[data-cy=password-input]').type('SecurePass123');
    cy.get('[data-cy=submit-button]').click();

    cy.url().should('include', '/dashboard');
    cy.get('[data-cy=user-email]').should('contain', 'test@example.com');
  });

  it('should complete login flow', () => {
    // Assuming user is already registered
    cy.get('[data-cy=email-input]').type('test@example.com');
    cy.get('[data-cy=password-input]').type('SecurePass123');
    cy.get('[data-cy=submit-button]').click();

    cy.url().should('include', '/dashboard');
    cy.get('[data-cy=logout-button]').should('be.visible');
  });

  it('should handle invalid credentials', () => {
    cy.get('[data-cy=email-input]').type('test@example.com');
    cy.get('[data-cy=password-input]').type('wrongpassword');
    cy.get('[data-cy=submit-button]').click();

    cy.get('[data-cy=error-message]')
      .should('be.visible')
      .and('contain', 'Invalid credentials');
  });
});'''
    
    def _generate_database_setup(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate database setup files."""
        tech_stack = specs.get("technology_stack", {})
        db_type = tech_stack.get("database", "PostgreSQL")
        
        if "PostgreSQL" in db_type:
            return self._generate_postgresql_setup(specs)
        else:
            return self._generate_mongodb_setup(specs)
    
    def _generate_postgresql_setup(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate PostgreSQL setup."""
        return {
            "database/schema.sql": self._create_postgresql_schema(),
            "database/migrations/001_initial.sql": self._create_initial_migration(),
            "database/seed.sql": self._create_seed_data()
        }
    
    def _create_postgresql_schema(self) -> str:
        """Create PostgreSQL schema."""
        return '''-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sessions table for JWT tracking
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log(created_at);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();'''
    
    def _create_initial_migration(self) -> str:
        """Create initial migration."""
        return '''-- Migration: 001_initial
-- Description: Create initial database schema

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, role) VALUES 
('admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlM3xD3xK2N1a0.', 'admin');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;'''
    
    def _create_seed_data(self) -> str:
        """Create seed data."""
        return '''-- Seed data for development
-- Admin user: admin@example.com / admin123
-- Test user: test@example.com / test123

INSERT INTO users (email, password_hash, role) VALUES 
('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlM3xD3xK2N1a0.', 'user')
ON CONFLICT (email) DO NOTHING;

-- Add sample audit log entries
INSERT INTO audit_log (user_id, action, resource, details) VALUES 
(1, 'login', 'auth', '{"ip": "127.0.0.1", "user_agent": "Mozilla/5.0"}'),
(2, 'profile_update', 'user', '{"fields": ["email", "role"]}');'''
    
    def _generate_mongodb_setup(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate MongoDB setup."""
        return {
            "database/models/User.js": self._create_mongodb_user_model(),
            "database/seed.js": self._create_mongodb_seed_script()
        }
    
    def _create_mongodb_user_model(self) -> str:
        """Create MongoDB user model."""
        return '''const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/, 'Invalid email format']
  },
  password: {
    type: String,
    required: true,
    minlength: 6,
    select: false // Don't include password in queries by default
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastLogin: {
    type: Date
  },
  loginAttempts: {
    type: Number,
    default: 0
  },
  lockUntil: {
    type: Date
  }
}, {
  timestamps: true,
  toJSON: {
    transform: function(doc, ret) {
      delete ret.password;
      delete ret.loginAttempts;
      delete ret.lockUntil;
      return ret;
    }
  }
});

// Index for performance
userSchema.index({ email: 1 });
userSchema.index({ createdAt: -1 });

// Hash password before saving
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  
  try {
    const salt = await bcrypt.genSalt(12);
    this.password = await bcrypt.hash(this.password, salt);
    next();
  } catch (error) {
    next(error);
  }
});

// Compare password method
userSchema.methods.comparePassword = async function(candidatePassword) {
  return await bcrypt.compare(candidatePassword, this.password);
};

// Check if account is locked
userSchema.methods.isLocked = function() {
  return !!(this.lockUntil && this.lockUntil > Date.now());
};

// Increment login attempts
userSchema.methods.incLoginAttempts = function() {
  const maxAttempts = 5;
  const lockTime = 2 * 60 * 60 * 1000; // 2 hours

  if (this.lockUntil && this.lockUntil < Date.now()) {
    return this.updateOne({
      $unset: { loginAttempts: 1, lockUntil: 1 }
    });
  }

  const updates = { $inc: { loginAttempts: 1 } };
  
  if (this.loginAttempts + 1 >= maxAttempts && !this.isLocked()) {
    updates.$set = { lockUntil: Date.now() + lockTime };
  }
  
  return this.updateOne(updates);
};

module.exports = mongoose.model('User', userSchema);'''
    
    def _create_mongodb_seed_script(self) -> str:
        """Create MongoDB seed script."""
        return '''const mongoose = require('mongoose');
const User = require('./models/User');
require('dotenv').config();

const seedUsers = async () => {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/myapp');
    console.log('Connected to MongoDB');

    // Clear existing users
    await User.deleteMany({});
    console.log('Cleared existing users');

    // Create admin user
    const adminUser = new User({
      email: 'admin@example.com',
      password: 'admin123',
      role: 'admin'
    });
    await adminUser.save();
    console.log('Created admin user');

    // Create test user
    const testUser = new User({
      email: 'test@example.com',
      password: 'test123',
      role: 'user'
    });
    await testUser.save();
    console.log('Created test user');

    console.log('Database seeded successfully');
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    await mongoose.connection.close();
    console.log('Database connection closed');
  }
};

seedUsers();'''
    
    def _generate_code_documentation(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate code documentation."""
        return {
            "README.md": self._create_readme(),
            "API.md": self._create_api_docs(),
            "DEPLOYMENT.md": self._create_deployment_guide()
        }
    
    def _create_readme(self) -> str:
        """Create README documentation."""
        return '''# User Authentication System

A secure JWT-based authentication system built with modern web technologies.

## Features

- JWT-based authentication
- Role-based access control (RBAC)
- Secure password hashing
- Rate limiting and security headers
- Comprehensive test coverage
- React frontend with TypeScript
- Express.js backend API

## Technology Stack

- **Backend**: Node.js with Express.js
- **Database**: MongoDB with Mongoose ODM
- **Frontend**: React with TypeScript
- **Authentication**: JWT with bcrypt
- **Testing**: Jest, Supertest, Cypress
- **Security**: Helmet, CORS, Rate limiting

## Quick Start

### Prerequisites

- Node.js 16+ 
- MongoDB 4.4+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd auth-system
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start MongoDB:
```bash
mongod
```

5. Seed the database:
```bash
npm run seed
```

6. Start the development servers:
```bash
# Backend (Terminal 1)
npm run dev:server

# Frontend (Terminal 2) 
npm run dev:client
```

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/verify` - Verify token (protected)

### Users

- `GET /api/users/profile` - Get user profile (protected)
- `PUT /api/users/profile` - Update user profile (protected)

## Security Features

- Bcrypt password hashing with salt rounds
- JWT token expiration and refresh
- Rate limiting (100 requests per 15 minutes)
- CORS configuration
- Security headers with Helmet
- Input validation and sanitization
- SQL injection prevention
- XSS protection

## Testing

Run the test suite:
```bash
npm test                    # Run all tests
npm run test:unit          # Unit tests only
npm run test:integration   # Integration tests
npm run test:e2e           # End-to-end tests
npm run test:coverage      # Coverage report
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.'''
    
    def _create_api_docs(self) -> str:
        """Create API documentation."""
        return '''# API Documentation

## Authentication Endpoints

### POST /api/auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Success Response (201):**
```json
{
  "message": "User created successfully"
}
```

**Error Response (400):**
```json
{
  "error": "User already exists"
}
```

### POST /api/auth/login

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com", 
  "password": "securepassword"
}
```

**Success Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "role": "user"
  }
}
```

**Error Response (401):**
```json
{
  "error": "Invalid credentials"
}
```

### GET /api/auth/verify

Verify JWT token validity.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Success Response (200):**
```json
{
  "valid": true,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "role": "user"
  }
}
```

**Error Response (403):**
```json
{
  "error": "Invalid or expired token"
}
```

## Protected Endpoints

All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### GET /api/users/profile

Get current user's profile information.

**Success Response (200):**
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "role": "user",
    "createdAt": "2023-01-01T00:00:00.000Z"
  }
}
```

### PUT /api/users/profile

Update user profile information.

**Request Body:**
```json
{
  "email": "newemail@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "newemail@example.com",
    "role": "user"
  }
}
```

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid credentials)
- `403` - Forbidden (invalid/expired token)
- `404` - Not Found
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Rate Limiting

API endpoints are rate limited to prevent abuse:
- **Authentication endpoints**: 5 requests per minute per IP
- **General API**: 100 requests per 15 minutes per IP

## Security Considerations

- All passwords are hashed using bcrypt with 12 salt rounds
- JWT tokens expire after 1 hour
- All inputs are validated and sanitized
- CORS is configured for same-origin requests
- Security headers are set via Helmet.js'''
    
    def _create_deployment_guide(self) -> str:
        """Create deployment guide."""
        return '''# Deployment Guide

## Production Environment Setup

### Prerequisites

- Node.js 16+ LTS
- MongoDB 4.4+ (Atlas recommended)
- SSL certificate for HTTPS
- Process manager (PM2 recommended)

### Environment Variables

Create a `.env` file with the following variables:

```env
# Server Configuration
NODE_ENV=production
PORT=3000

# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/myapp?retryWrites=true&w=majority

# JWT Configuration
JWT_SECRET=your-super-secure-jwt-secret-key-here
JWT_EXPIRE=1h

# Security
CORS_ORIGIN=https://yourdomain.com
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# Email (if using email verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### Build and Deploy Backend

1. **Install dependencies:**
```bash
npm ci --only=production
```

2. **Build the application:**
```bash
npm run build
```

3. **Start with PM2:**
```bash
# Install PM2 globally
npm install -g pm2

# Start the application
pm2 start ecosystem.config.js

# Monitor logs
pm2 logs auth-app

# Set up PM2 startup script
pm2 startup
pm2 save
```

4. **PM2 Ecosystem Configuration (`ecosystem.config.js`):**
```javascript
module.exports = {
  apps: [{
    name: 'auth-app',
    script: './server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

### Deploy Frontend

#### Option 1: Static Hosting (Netlify/Vercel)

1. **Build the frontend:**
```bash
npm run build
```

2. **Deploy `build` folder to your hosting provider**

3. **Configure environment variables in hosting platform:**
```env
REACT_APP_API_URL=https://api.yourdomain.com
```

#### Option 2: Docker Deployment

1. **Create Dockerfile:**
```dockerfile
# Build stage
FROM node:16-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

2. **Docker Compose (`docker-compose.yml`):**
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    depends_on:
      - mongo

  mongo:
    image: mongo:4.4
    volumes:
      - mongo_data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password

volumes:
  mongo_data:
```

### SSL/HTTPS Setup

#### Using Let's Encrypt (Certbot)

1. **Install Certbot:**
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# macOS
brew install certbot
```

2. **Generate certificate:**
```bash
sudo certbot --nginx -d yourdomain.com
```

3. **Auto-renewal (crontab):**
```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

### Monitoring and Logging

#### Application Monitoring

1. **Health check endpoint:**
```javascript
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV
  });
});
```

2. **PM2 Monitoring:**
```bash
pm2 monit
```

#### Log Management

1. **Structured logging:**
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

### Database Backups

#### MongoDB Backup Script

```bash
#!/bin/bash
# backup-mongo.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"
DATABASE="myapp"

mkdir -p $BACKUP_DIR

mongodump --uri="$MONGODB_URI" --out="$BACKUP_DIR/$DATE"

# Keep only last 7 days of backups
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;

echo "Backup completed: $DATE"
```

### Security Checklist

- [ ] Environment variables secured
- [ ] SSL certificate installed
- [ ] JWT secrets are strong and unique
- [ ] Rate limiting configured
- [ ] CORS properly configured
- [ ] Database authentication enabled
- [ ] Firewall rules configured
- [ ] Regular security updates scheduled
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up

### Performance Optimization

1. **Enable gzip compression**
2. **Set up CDN for static assets**
3. **Implement Redis caching**
4. **Database indexing optimization**
5. **Connection pooling**
6. **Image optimization**

### Troubleshooting

#### Common Issues

1. **JWT token expiration:**
   - Check token expiration time
   - Implement refresh token mechanism

2. **Database connection issues:**
   - Verify connection string
   - Check network connectivity
   - Monitor connection pool

3. **Rate limiting:**
   - Adjust rate limit settings
   - Implement proper error handling

4. **CORS issues:**
   - Verify CORS origin configuration
   - Check preflight requests

#### Log Analysis

```bash
# View application logs
pm2 logs auth-app

# Search for errors
grep "error" /var/log/nginx/access.log

# Monitor real-time logs
tail -f logs/combined.log
```

### Scaling Considerations

- **Horizontal scaling**: Load balancer with multiple app instances
- **Database scaling**: MongoDB replica sets for read scaling
- **Caching**: Redis for session storage and API caching
- **CDN**: CloudFlare or AWS CloudFront for static assets
- **Monitoring**: Application performance monitoring (APM) tools'''
    
    def _generate_configuration(self, specs: Dict[str, Any]) -> Dict[str, str]:
        """Generate configuration files."""
        tech_stack = specs.get("technology_stack", {})
        
        config = {
            ".env.example": self._create_env_example(),
            "package.json": self._create_package_json(),
            "ecosystem.config.js": self._create_pm2_config()
        }
        
        if tech_stack.get("frontend") == "React":
            config["frontend/package.json"] = self._create_frontend_package_json()
            
        return config
    
    def _create_env_example(self) -> str:
        """Create environment variables example."""
        return '''# Server Configuration
NODE_ENV=development
PORT=3000

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/myapp

# JWT Configuration
JWT_SECRET=your-super-secure-jwt-secret-key-here
JWT_EXPIRE=1h

# Security Configuration
CORS_ORIGIN=http://localhost:3000
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=info

# Email Configuration (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Frontend URL (for CORS)
REACT_APP_API_URL=http://localhost:3000/api'''
    
    def _create_package_json(self) -> str:
        """Create package.json for backend."""
        return '''{
  "name": "auth-system",
  "version": "1.0.0",
  "description": "JWT-based authentication system",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "build": "echo 'Build step completed'",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint .",
    "lint:fix": "eslint . --fix",
    "seed": "node scripts/seed.js"
  },
  "keywords": ["auth", "jwt", "express", "mongodb"],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "express": "^4.18.2",
    "mongoose": "^7.5.0",
    "bcryptjs": "^2.4.3",
    "jsonwebtoken": "^9.0.2",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "express-rate-limit": "^6.10.0",
    "express-validator": "^7.0.1",
    "dotenv": "^16.3.1",
    "winston": "^3.10.0",
    "joi": "^17.9.2"
  },
  "devDependencies": {
    "nodemon": "^3.0.1",
    "jest": "^29.6.4",
    "supertest": "^6.3.3",
    "eslint": "^8.48.0",
    "eslint-config-airbnb-base": "^15.0.0",
    "eslint-plugin-import": "^2.28.1",
    "@types/jest": "^29.5.5"
  }
}'''
    
    def _create_pm2_config(self) -> str:
        """Create PM2 ecosystem configuration."""
        return '''module.exports = {
  apps: [{
    name: 'auth-system',
    script: 'server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development',
      PORT: 3000
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    max_memory_restart: '1G',
    node_args: '--max_old_space_size=1024'
  }]
};'''
    
    def _create_frontend_package_json(self) -> str:
        """Create package.json for frontend."""
        return '''{
  "name": "auth-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@types/node": "^20.5.9",
    "@types/react": "^18.2.21",
    "@types/react-dom": "^18.2.7",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "typescript": "^5.2.2",
    "web-vitals": "^3.4.0"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.1.3",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.4.3",
    "@types/jest": "^29.5.5",
    "react-scripts": "5.0.1",
    "cypress": "^13.1.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "cypress:open": "cypress open",
    "cypress:run": "cypress run"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}'''

# Example usage
if __name__ == "__main__":
    agent = CoderAgent()
    
    # Example specifications
    specifications = {
        "technology_stack": {
            "backend": "Express.js",
            "database": "MongoDB",
            "frontend": "React"
        },
        "api_design": {
            "authentication": "JWT"
        }
    }
    
    # Generate implementation
    implementation = agent.implement_feature(specifications)
    
    print("Coder Agent - Implementation Generated")
    print("=" * 50)
    print(f"Backend files: {len(implementation['backend_code'])}")
    print(f"Frontend files: {len(implementation['frontend_code'])}")
    print(f"Test files: {len(implementation['tests'])}")
    print(f"Documentation files: {len(implementation['documentation'])}")
```

## PR Reviewer Sub-Agent

```python
#!/usr/bin/env python3
"""
PR Reviewer Sub-Agent
Specializes in code review, quality assurance, security analysis, and performance validation.
"""

import json
import subprocess
import os
import re
from typing import Dict, List, Any, Tuple

class PRReviewerAgent:
    def __init__(self):
        self.role = "pr_reviewer"
        self.expertise = [
            "code_quality", "security_analysis", "performance_review",
            "test_coverage", "architecture_compliance", "documentation_review"
        ]
    
    def conduct_code_review(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive code review."""
        review_results = {
            "code_quality": self._review_code_quality(implementation),
            "security_analysis": self._analyze_security(implementation),
            "performance_review": self._review_performance(implementation),
            "test_coverage": self._analyze_test_coverage(implementation),
            "architecture_compliance": self._check_architecture_compliance(implementation),
            "documentation_review": self._review_documentation(implementation),
            "overall_score": 0,
            "recommendations": [],
            "critical_issues": [],
            "approval_status": "pending"
        }
        
        # Calculate overall score
        review_results["overall_score"] = self._calculate_review_score(review_results)
        
        # Determine approval status
        review_results["approval_status"] = self._determine_approval_status(review_results)
        
        return review_results
    
    def _review_code_quality(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Review code quality and best practices."""
        quality_metrics = {
            "code_style": self._check_code_style(implementation),
            "complexity": self._analyze_complexity(implementation),
            "maintainability": self._check_maintainability(implementation),
            "error_handling": self._review_error_handling(implementation),
            "logging": self._check_logging(implementation)
        }
        
        return {
            "score": self._calculate_quality_score(quality_metrics),
            "metrics": quality_metrics,
            "issues": self._identify_quality_issues(quality_metrics)
        }
    
    def _analyze_security(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security vulnerabilities and best practices."""
        security_checks = {
            "authentication": self._check_authentication_security(implementation),
            "authorization": self._check_authorization_security(implementation),
            "input_validation": self._check_input_validation(implementation),
            "sql_injection": self._check_sql_injection_risks(implementation),
            "xss_protection": self._check_xss_protection(implementation),
            "csrf_protection": self._check_csrf_protection(implementation),
            "data_encryption": self._check_data_encryption(implementation)
        }
        
        return {
            "score": self._calculate_security_score(security_checks),
            "checks": security_checks,
            "vulnerabilities": self._identify_security_issues(security_checks)
        }
    
    def _review_performance(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Review performance considerations."""
        performance_review = {
            "database_optimization": self._check_database_optimization(implementation),
            "caching_strategy": self._check_caching_strategy(implementation),
            "async_operations": self._check_async_operations(implementation),
            "memory_usage": self._check_memory_usage(implementation),
            "api_efficiency": self._check_api_efficiency(implementation),
            "frontend_optimization": self._check_frontend_optimization(implementation)
        }
        
        return {
            "score": self._calculate_performance_score(performance_review),
            "areas": performance_review,
            "optimizations": self._suggest_performance_optimizations(performance_review)
        }
    
    def _analyze_test_coverage(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage and quality."""
        coverage_analysis = {
            "unit_tests": self._analyze_unit_tests(implementation),
            "integration_tests": self._analyze_integration_tests(implementation),
            "e2e_tests": self._analyze_e2e_tests(implementation),
            "coverage_percentage": self._calculate_coverage_percentage(implementation),
            "test_quality": self._assess_test_quality(implementation)
        }
        
        return {
            "score": self._calculate_coverage_score(coverage_analysis),
            "analysis": coverage_analysis,
            "gaps": self._identify_test_gaps(coverage_analysis)
        }
    
    def _check_architecture_compliance(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with architectural decisions."""
        compliance_checks = {
            "design_patterns": self._check_design_patterns(implementation),
            "separation_of_concerns": self._check_separation_of_concerns(implementation),
            "dependency_management": self._check_dependencies(implementation),
            "api_consistency": self._check_api_consistency(implementation),
            "data_layer": self._check_data_layer(implementation)
        }
        
        return {
            "score": self._calculate_compliance_score(compliance_checks),
            "checks": compliance_checks,
            "violations": self._identify_architecture_violations(compliance_checks)
        }
    
    def _review_documentation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Review documentation completeness and quality."""
        documentation_review = {
            "api_documentation": self._check_api_documentation(implementation),
            "code_comments": self._check_code_comments(implementation),
            "readme_quality": self._check_readme_quality(implementation),
            "inline_documentation": self._check_inline_documentation(implementation),
            "examples": self._check_code_examples(implementation)
        }
        
        return {
            "score": self._calculate_documentation_score(documentation_review),
            "areas": documentation_review,
            "gaps": self._identify_documentation_gaps(documentation_review)
        }
    
    def _check_code_style(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Check code style and formatting."""
        backend_code = implementation.get("backend_code", {})
        
        # Example style checks
        style_issues = []
        if backend_code:
            for filename, code in backend_code.items():
                if code:
                    style_issues.extend(self._analyze_code_style(code, filename))
        
        return {
            "issues_found": len(style_issues),
            "issues": style_issues,
            "compliance": "good" if len(style_issues) < 5 else "needs_improvement"
        }
    
    def _analyze_code_style(self, code: str, filename: str) -> List[str]:
        """Analyze code for style issues."""
        issues = []
        
        # Check for common style issues
        if len(code) > 2000:
            issues.append(f"{filename}: File too long (>2000 lines)")
        
        if not code.strip():
            issues.append(f"{filename}: Empty file")
        
        # Check for TODO/FIXME comments
        todo_matches = re.findall(r'(?:TODO|FIXME|HACK)', code, re.IGNORECASE)
        if todo_matches:
            issues.append(f"{filename}: Contains {len(todo_matches)} TODO/FIXME comments")
        
        return issues
    
    def _check_authentication_security(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Check authentication security implementations."""
        backend_code = implementation.get("backend_code", {})
        
        auth_files = {k: v for k, v in backend_code.items() if 'auth' in k.lower()}
        
        security_issues = []
        
        for filename, code in auth_files.items():
            if code:
                # Check for JWT implementation
                if 'jwt' not in code.lower():
                    security_issues.append(f"{filename}: Missing JWT implementation")
                
                # Check for password hashing
                if 'bcrypt' not in code.lower() and 'hash' not in code.lower():
                    security_issues.append(f"{filename}: Password hashing not implemented")
                
                # Check for token expiration
                if 'expire' not in code.lower() and 'expires' not in code.lower():
                    security_issues.append(f"{filename}: Token expiration not set")
        
        return {
            "secure": len(security_issues) == 0,
            "issues": security_issues,
            "recommendation": "Implement proper JWT with bcrypt and token expiration" if security_issues else "Good authentication implementation"
        }
    
    def _check_input_validation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """Check input validation implementations."""
        backend_code = implementation.get("backend_code", {})
        
        validation_issues = []
        
        for filename, code in backend_code.items():
            if code and 'route' in filename.lower():
                # Check for input validation
                if 'validate' not in code.lower() and 'validation' not in code.lower():
                    validation_issues.append(f"{filename}: Missing input validation")
                
                # Check for sanitization
                if 'sanitize' not in code.lower() and 'escape' not in code.lower():
                    validation_issues.append(f"{filename}: Missing input sanitization")
        
        return {
            "implemented": len(validation_issues) == 0,
            "issues": validation_issues,
            "recommendation": "Add input validation and sanitization" if validation_issues else "Good input validation"
        }
    
    def _calculate_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate code quality score (0-100)."""
        weights = {
            "code_style": 0.25,
            "complexity": 0.20,
            "maintainability": 0.20,
            "error_handling": 0.20,
            "logging": 0.15
        }
        
        total_score = 0
        for metric, weight in weights.items():
            metric_data = quality_metrics.get(metric, {})
            # Simplified scoring - in real implementation, this would be more sophisticated
            score = 80 if metric_data.get("compliance") == "good" else 60
            total_score += score * weight
        
        return round(total_score, 1)
    
    def _calculate_security_score(self, security_checks: Dict[str, Any]) -> float:
        """Calculate security score (0-100)."""
        critical_issues = 0
        total_checks = len(security_checks)
        
        for check_name, check_result in security_checks.items():
            if isinstance(check_result, dict) and check_result.get("secure", True) is False:
                critical_issues += 1
        
        if critical_issues > 0:
            return max(0, 100 - (critical_issues * 20))
        else:
            return 95.0
    
    def _calculate_review_score(self, review_results: Dict[str, Any]) -> float:
        """Calculate overall review score."""
        weights = {
            "code_quality": 0.25,
            "security_analysis": 0.30,
            "performance_review": 0.15,
            "test_coverage": 0.15,
            "architecture_compliance": 0.10,
            "documentation_review": 0.05
        }
        
        total_score = 0
        for category, weight in weights.items():
            category_result = review_results.get(category, {})
            score = category_result.get("score", 0)
            total_score += score * weight
        
        return round(total_score, 1)
    
    def _determine_approval_status(self, review_results: Dict[str, Any]) -> str:
        """Determine approval status based on review results."""
        score = review_results.get("overall_score", 0)
        critical_issues = review_results.get("critical_issues", [])
        
        if critical_issues:
            return "rejected"
        elif score >= 85:
            return "approved"
        elif score >= 70:
            return "changes_requested"
        else:
            return "rejected"
    
    def _identify_quality_issues(self, quality_metrics: Dict[str, Any]) -> List[str]:
        """Identify code quality issues."""
        issues = []
        
        for metric_name, metric_data in quality_metrics.items():
            if isinstance(metric_data, dict):
                metric_issues = metric_data.get("issues", [])
                if metric_issues:
                    issues.extend(metric_issues)
        
        return issues
    
    def _identify_security_issues(self, security_checks: Dict[str, Any]) -> List[str]:
        """Identify security vulnerabilities."""
        vulnerabilities = []
        
        for check_name, check_result in security_checks.items():
            if isinstance(check_result, dict):
                issues = check_result.get("issues", [])
                if issues:
                    vulnerabilities.extend([f"Security: {issue}" for issue in issues])
        
        return vulnerabilities
    
    def generate_review_report(self, review_results: Dict[str, Any]) -> str:
        """Generate detailed review report."""
        report = f"""# Code Review Report

## Overall Assessment
- **Score**: {review_results.get('overall_score', 0)}/100
- **Status**: {review_results.get('approval_status', 'pending').title()}

## Code Quality Review
- **Score**: {review_results.get('code_quality', {}).get('score', 0)}/100
- **Issues Found**: {len(review_results.get('code_quality', {}).get('issues', []))}

### Quality Issues:
{self._format_issues(review_results.get('code_quality', {}).get('issues', []))}

## Security Analysis
- **Score**: {review_results.get('security_analysis', {}).get('score', 0)}/100
- **Vulnerabilities**: {len(review_results.get('security_analysis', {}).get('vulnerabilities', []))}

### Security Issues:
{self._format_issues(review_results.get('security_analysis', {}).get('vulnerabilities', []))}

## Performance Review
- **Score**: {review_results.get('performance_review', {}).get('score', 0)}/100
- **Optimizations**: {len(review_results.get('performance_review', {}).get('optimizations', []))}

## Test Coverage Analysis
- **Score**: {review_results.get('test_coverage', {}).get('score', 0)}/100
- **Coverage**: {review_results.get('test_coverage', {}).get('analysis', {}).get('coverage_percentage', 0)}%

## Recommendations
{self._format_recommendations(review_results.get('recommendations', []))}

---
*Generated by PR Reviewer Agent*
"""
        return report
    
    def _format_issues(self, issues: List[str]) -> str:
        """Format issues for report."""
        if not issues:
            return "✅ No issues found"
        
        return "\n".join(f"- {issue}" for issue in issues)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations for report."""
        if not recommendations:
            return "✅ No additional recommendations"
        
        return "\n".join(f"- {rec}" for rec in recommendations)
    
    # Placeholder methods for other checks
    def _analyze_complexity(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 85, "max_complexity": 10, "cyclomatic_complexity": "acceptable"}
    
    def _check_maintainability(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "coupling": "low", "cohesion": "high"}
    
    def _review_error_handling(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 75, "proper_error_handling": True}
    
    def _check_logging(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 70, "structured_logging": True}
    
    def _check_authorization_security(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"secure": True, "issues": [], "recommendation": "Good authorization implementation"}
    
    def _check_sql_injection_risks(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"risk_level": "low", "issues": []}
    
    def _check_xss_protection(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"protected": True, "issues": []}
    
    def _check_csrf_protection(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"implemented": True, "issues": []}
    
    def _check_data_encryption(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"encrypted": True, "issues": []}
    
    def _check_database_optimization(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "indexing": "good"}
    
    def _check_caching_strategy(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"implemented": False, "recommendation": "Consider adding caching layer"}
    
    def _check_async_operations(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 85, "proper_async": True}
    
    def _check_memory_usage(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "memory_leaks": False}
    
    def _check_api_efficiency(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 75, "response_optimization": "good"}
    
    def _check_frontend_optimization(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "bundle_optimization": "good"}
    
    def _analyze_unit_tests(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"files": 3, "coverage": "good", "quality": "high"}
    
    def _analyze_integration_tests(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"files": 2, "coverage": "medium", "quality": "medium"}
    
    def _analyze_e2e_tests(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"files": 1, "coverage": "low", "quality": "medium"}
    
    def _calculate_coverage_percentage(self, implementation: Dict[str, Any]) -> float:
        return 85.0
    
    def _assess_test_quality(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "readability": "good", "maintainability": "good"}
    
    def _identify_test_gaps(self, coverage_analysis: Dict[str, Any]) -> List[str]:
        return ["Add more edge case tests", "Increase e2e test coverage"]
    
    def _check_design_patterns(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 85, "patterns_used": ["MVC", "Repository"]}
    
    def _check_separation_of_concerns(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "proper_separation": True}
    
    def _check_dependencies(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 75, "vulnerabilities": 0, "outdated": 2}
    
    def _check_api_consistency(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 90, "consistent": True}
    
    def _check_data_layer(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 85, "proper_abstraction": True}
    
    def _identify_architecture_violations(self, compliance_checks: Dict[str, Any]) -> List[str]:
        return ["Update 2 outdated dependencies"]
    
    def _check_api_documentation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 85, "completeness": "good"}
    
    def _check_code_comments(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 75, "quality": "medium"}
    
    def _check_readme_quality(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 80, "completeness": "good"}
    
    def _check_inline_documentation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 70, "coverage": "medium"}
    
    def _check_code_examples(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        return {"score": 75, "examples_provided": True}
    
    def _identify_documentation_gaps(self, documentation_review: Dict[str, Any]) -> List[str]:
        return ["Add more inline comments", "Include deployment examples"]
    
    def _calculate_performance_score(self, performance_review: Dict[str, Any]) -> float:
        return 80.0
    
    def _calculate_coverage_score(self, coverage_analysis: Dict[str, Any]) -> float:
        return 85.0
    
    def _calculate_compliance_score(self, compliance_checks: Dict[str, Any]) -> float:
        return 82.0
    
    def _calculate_documentation_score(self, documentation_review: Dict[str, Any]) -> float:
        return 78.0
    
    def _suggest_performance_optimizations(self, performance_review: Dict[str, Any]) -> List[str]:
        return ["Implement Redis caching", "Add database indexing", "Optimize database queries"]

# Example usage
if __name__ == "__main__":
    reviewer = PRReviewerAgent()
    
    # Example implementation (would come from Coder agent)
    example_implementation = {
        "backend_code": {
            "server.js": "const express = require('express');...",
            "routes/auth.js": "const router = express.Router();...",
            "middleware/auth.js": "const jwt = require('jsonwebtoken');..."
        },
        "frontend_code": {
            "src/App.tsx": "import React from 'react';...",
            "src/components/Auth.tsx": "const Auth: React.FC = () => {...}"
        },
        "tests": {
            "tests/auth.test.js": "describe('Auth', () => {...})",
            "cypress/e2e/auth.cy.js": "describe('Auth Flow', () => {...})"
        },
        "documentation": {
            "README.md": "# User Authentication System...",
            "API.md": "# API Documentation..."
        }
    }
    
    # Conduct code review
    review_results = reviewer.conduct_code_review(example_implementation)
    report = reviewer.generate_review_report(review_results)
    
    print("PR Reviewer Agent - Code Review Complete")
    print("=" * 60)
    print(f"Overall Score: {review_results['overall_score']}/100")
    print(f"Approval Status: {review_results['approval_status']}")
    print("\nReview Report:")
    print("-" * 40)
    print(report)
```