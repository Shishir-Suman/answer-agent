# Answer Agent Frontend

This is the frontend for the Answer Agent application, built with React, TypeScript, and Tailwind CSS.

## Setup and Installation

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm run dev
   ```

3. Build for production:
   ```
   npm run build
   ```

## Structure

- `src/`: Source code
  - `components/`: React components
    - `ChatInterface.tsx`: Main chat interface component
    - `Header.tsx`: Application header
    - `MessageItem.tsx`: Individual message component
  - `services/`: API services
    - `api.ts`: API client for backend communication
  - `main.tsx`: Application entry point
  - `App.tsx`: Main application component
  - `index.css`: Global styles with Tailwind

## Development

- The frontend communicates with the backend via the `/api/query` endpoint
- All API calls are made through the API service in `services/api.ts`
- The application uses Tailwind CSS for styling
- TypeScript is used for type safety

## API Communication

The frontend sends queries to the backend API endpoint `/api/query` with the structure:

```json
{
  "query": "Your query text here"
}
```

The backend responds with:

```json
{
  "response": "The response text from the AI"
}
```

## Troubleshooting

- If you encounter CORS issues, ensure the backend is properly configured with CORS headers
- Check the browser console for any errors
- Verify that the backend server is running and accessible 