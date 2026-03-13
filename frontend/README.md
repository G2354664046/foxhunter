# FoxHunter Frontend

Vue.js 3 frontend for the FoxHunter malware detection system.

## Features

- Vue 3 Composition API
- Vue Router for navigation
- Pinia for state management
- ECharts for data visualization
- Tailwind CSS for styling
- JWT 登录态（本地存储 Token，自动携带 Authorization 头）
- Interactive file upload with drag & drop
- Real-time detection status
- Responsive design with dark theme
- Animated background effects

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/
│   │   └── main.css       # Global styles with Tailwind
│   ├── components/
│   │   └── Header.vue     # Navigation component
│   ├── views/
│   │   ├── Home.vue       # Landing page with upload interface
│   │   ├── Upload.vue     # File upload page
│   │   └── Results.vue    # Detection results page
│   ├── router/
│   │   └── index.js       # Vue Router configuration
│   ├── stores/
│   │   └── sample.js      # Pinia store for sample management
│   ├── App.vue            # Root component
│   └── main.js            # Application entry
├── package.json
├── vite.config.js
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── index.html             # HTML entry point
└── README.md
```

## Installation

```bash
cd frontend
npm install
```

## Development

```bash
npm run dev
```

The development server will start at `http://localhost:5173` and proxy API requests to the FastAPI backend.

## Build

```bash
npm run build
```

## Features Overview

### Home Page
- Interactive landing page with animated starfield and fireflies
- Tab-based interface for different scan types (File, URL, Hash)
- Drag & drop file upload with visual feedback
- Real-time statistics display
- Feature showcase with scroll animations

### File Upload
- Drag & drop interface with hover effects
- File type validation (.exe, .dll, .bin)
- Real-time upload progress
- Integration with backend API

### Results Display
- Detection status tracking
- Confidence score visualization
- Model comparison (Random Forest vs CNN) with bar chart powered by ECharts
- Detailed scan results with progress bars

## API Integration

The frontend communicates with the FastAPI backend through:

- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login (get JWT access_token)
- `GET /api/v1/auth/me` - Current user
- `POST /api/v1/upload` - File upload endpoint
- `GET /api/v1/result/{sample_id}` - Results retrieval

## Styling

- **Tailwind CSS**: Utility-first CSS framework
- **Custom CSS Variables**: Consistent theming
- **Animations**: Smooth transitions and micro-interactions
- **Responsive Design**: Mobile-first approach
- **Dark Theme**: Cyberpunk-inspired design

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## API Integration

The frontend communicates with the FastAPI backend through the following endpoints:

- `POST /api/v1/upload` - Upload file for scanning
- `GET /api/v1/result/{sample_id}` - Get scan results