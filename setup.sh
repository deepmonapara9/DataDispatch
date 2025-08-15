#!/bin/bash

# AI Newsletter Platform Setup Script
# This script sets up the complete newsletter platform

set -e  # Exit on any error

echo "🚀 Setting up AI Newsletter Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        print_success "Python 3 is installed"
        python3 --version
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if Node.js is installed (optional, for frontend development)
check_node() {
    if command -v node &> /dev/null; then
        print_success "Node.js is installed"
        node --version
    else
        print_warning "Node.js not found. It's optional but recommended for frontend development."
    fi
}

# Create virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [ ! -d "backend/venv" ]; then
        cd backend
        python3 -m venv venv
        cd ..
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    cd backend
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
    
    print_success "Python dependencies installed"
}

# Setup environment file
setup_env_file() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your actual configuration:"
        print_warning "  - Set SMTP_EMAIL and SMTP_PASSWORD for Gmail"
        print_warning "  - Set FRONTEND_URL for your deployed frontend"
        print_warning "  - Optionally set OPENAI_API_KEY for better AI content"
    else
        print_success "Environment file already exists"
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    cd backend
    source venv/bin/activate
    python database.py
    cd ..
    
    print_success "Database initialized"
}

# Test the system
test_system() {
    print_status "Testing the system..."
    
    # Test backend
    print_status "Testing backend..."
    cd backend
    source venv/bin/activate
    python -c "
import sys
sys.path.append('.')
from database import init_db
init_db()
print('✅ Database connection OK')
"
    cd ..
    
    # Test AI agent
    print_status "Testing AI agent..."
    cd ai_agent
    python -c "
import sys
sys.path.append('../backend')
from content_generator import ContentGenerator
generator = ContentGenerator()
connections = generator.test_ai_connection()
if any(connections.values()):
    print('✅ AI service connection OK')
else:
    print('⚠️  No AI services available, will use fallback content')
"
    cd ..
    
    print_success "System test completed"
}

# Start development server
start_dev_server() {
    print_status "Starting development server..."
    print_warning "Make sure you have configured your .env file first!"
    
    cd backend
    source venv/bin/activate
    echo "🌐 Starting FastAPI server on http://localhost:8000"
    echo "📧 API documentation: http://localhost:8000/docs"
    echo "🛑 Press Ctrl+C to stop the server"
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}

# Show usage information
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  setup     - Full setup (default)"
    echo "  install   - Install dependencies only"
    echo "  test      - Test the system"
    echo "  dev       - Start development server"
    echo "  help      - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0              # Full setup"
    echo "  $0 dev          # Start development server"
    echo "  $0 test         # Test system components"
}

# Main setup function
main_setup() {
    print_status "Starting full setup..."
    
    check_python
    check_node
    setup_python_env
    install_python_deps
    setup_env_file
    init_database
    test_system
    
    print_success "Setup completed! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your configuration"
    echo "2. Run './setup.sh dev' to start the development server"
    echo "3. Open frontend/index.html in a browser"
    echo "4. Test the subscribe/unsubscribe functionality"
    echo ""
    echo "For production deployment, see README.md"
}

# Parse command line arguments
case "${1:-setup}" in
    "setup")
        main_setup
        ;;
    "install")
        check_python
        setup_python_env
        install_python_deps
        print_success "Dependencies installed"
        ;;
    "test")
        test_system
        ;;
    "dev")
        start_dev_server
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac
