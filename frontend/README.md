# WebScraper Frontend

A modern Next.js dashboard for the WebScraper application built with TypeScript, Tailwind CSS, and component-driven architecture.

## Features

- 📊 **Interactive Dashboard** - Real-time overview of scraping activities
- 🎨 **Modern UI Components** - Built with Tailwind CSS and custom components
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🔧 **Component-Driven** - Modular and reusable component architecture
- ⚡ **Fast Development** - Hot reload and TypeScript support
- 🎯 **Type Safety** - Full TypeScript integration

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Copy environment variables:
```bash
cp .env.example .env.local
```

3. Start the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
src/
├── app/                 # Next.js App Router
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Home page
├── components/         # React components
│   ├── ui/            # Reusable UI components
│   ├── dashboard/     # Dashboard-specific components
│   ├── Dashboard.tsx  # Main dashboard component
│   ├── Header.tsx     # Header component
│   └── Sidebar.tsx    # Sidebar navigation
└── lib/               # Utility functions
    └── utils.ts       # Common utilities
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Key Components

### Dashboard Components

- **StatCard** - Display key metrics with icons and trend indicators
- **RecentActivity** - Show recent scraping activities and their status
- **ProjectOverview** - Manage and monitor active scraping projects
- **ChartPlaceholder** - Placeholder for future chart integration

### UI Components

- **Card** - Flexible container component
- **Button** - Customizable button with multiple variants
- **Badge** - Status indicators and labels

## Future Integrations

This dashboard is prepared for integration with:

- **Backend API** - Connect to Django REST API
- **Real-time Updates** - WebSocket integration for live data
- **Authentication** - User management and session handling
- **Charts & Analytics** - Data visualization libraries
- **Database Integration** - Direct connection to scraped data

## Styling

The project uses Tailwind CSS with a custom design system:

- **Color Palette** - Consistent color variables
- **Component Variants** - Multiple styles for each component
- **Responsive Design** - Mobile-first approach
- **Dark Mode Ready** - CSS variables for theme switching

## Contributing

1. Follow the existing component structure
2. Use TypeScript for type safety
3. Follow the established naming conventions
4. Write clean, readable code with proper documentation

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better developer experience
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful and consistent icons
- **ESLint** - Code linting and formatting