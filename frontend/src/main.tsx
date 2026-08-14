import { createRoot } from 'react-dom/client'
import './index.css'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthLogsPage } from './AuthLogsPage.tsx';

const queryClient = new QueryClient();                    // ← the memory

createRoot(document.getElementById('root')!).render(
  <QueryClientProvider client={queryClient}>              
    <AuthLogsPage />
  </QueryClientProvider>
);
