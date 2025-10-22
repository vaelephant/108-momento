# Momento

A modern, minimalist photo management web application with timeline and category views.

## Overview

Momento is an elegant photo gallery application that allows users to upload, organize, and browse their photos through an intuitive interface. Inspired by clean, minimalist design principles, it provides a seamless experience for managing your photo collection.

## Features

### Core Functionality
- **Drag & Drop Upload**: Simple and intuitive photo upload by dragging files or clicking to select
- **Timeline View**: Browse photos organized chronologically by year and month
- **Category View**: Filter photos by categories (Nature, City, Portrait, Food, Travel, Other)
- **Tag Cloud**: Automatically generated tag cloud showing popular tags with frequency-based sizing
- **Masonry Grid Layout**: Beautiful responsive grid that adapts to different screen sizes

### Design Highlights
- **Dark Mode**: Elegant dark theme optimized for photo viewing
- **Minimalist UI**: Clean interface that puts photos front and center
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Smooth Animations**: Subtle transitions and hover effects for enhanced UX

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **UI Components**: shadcn/ui
- **State Management**: Custom store with React's useSyncExternalStore
- **Icons**: Lucide React

## Project Structure

\`\`\`
momento/
├── app/
│   ├── layout.tsx          # Root layout with metadata
│   ├── page.tsx            # Main page with view switching
│   └── globals.css         # Global styles and theme tokens
├── components/
│   ├── logo.tsx            # Momento brand logo
│   ├── photo-upload.tsx    # Drag & drop upload component
│   ├── photo-card.tsx      # Individual photo card display
│   ├── timeline-view.tsx   # Timeline organized view
│   ├── category-view.tsx   # Category filtered view
│   └── tag-cloud.tsx       # Dynamic tag cloud
├── lib/
│   ├── types.ts            # TypeScript type definitions
│   ├── mock-data.ts        # Sample photo data
│   └── photo-store.ts      # Photo state management
└── public/                 # Static photo assets
\`\`\`

## Installation

1. Clone the repository:
\`\`\`bash
git clone <repository-url>
cd momento
\`\`\`

2. Install dependencies:
\`\`\`bash
npm install
# or
pnpm install
# or
yarn install
\`\`\`

3. Run the development server:
\`\`\`bash
npm run dev
# or
pnpm dev
# or
yarn dev
\`\`\`

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Uploading Photos
1. Click the "Upload Photo" button in the top right corner
2. Drag and drop photos into the upload area, or click to select files
3. Photos will be automatically added to your gallery

### Viewing Photos
- **Timeline View**: Default view showing photos organized by date
- **Category View**: Switch tabs to browse by category
- **Tag Cloud**: Click tags in the sidebar to filter (coming soon)

### Navigation
- Use the sidebar to browse by year or category
- Click on any photo to view it in full size (coming soon)
- Hover over photos to see metadata

## Design Philosophy

Momento follows a minimalist design approach inspired by modern photo gallery applications:

- **Content First**: Photos are the hero, UI elements are subtle and unobtrusive
- **Dark Mode**: Optimized for photo viewing with reduced eye strain
- **Whitespace**: Generous spacing creates breathing room
- **Typography**: Clean, readable fonts with proper hierarchy
- **Interactions**: Smooth, purposeful animations that enhance rather than distract

## Future Enhancements

- [ ] Photo detail modal with full-size view
- [ ] Tag filtering functionality
- [ ] Search capability
- [ ] Photo editing tools
- [ ] Album creation
- [ ] Social sharing
- [ ] Database integration (Supabase/Neon)
- [ ] User authentication
- [ ] Cloud storage integration
- [ ] Bulk upload and management
- [ ] Export functionality

## Development Notes

### State Management
The app uses a custom store pattern with React's `useSyncExternalStore` for efficient state updates without external dependencies.

### Mock Data
Currently uses mock data for demonstration. The data structure is designed to easily integrate with a real backend.

### Responsive Grid
The masonry grid layout uses CSS columns for optimal performance and native browser support.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

---

Built with ❤️ using Next.js and Tailwind CSS
