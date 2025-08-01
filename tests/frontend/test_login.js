import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import Login from '../../frontend/src/components/Login';

// Mock fetch
global.fetch = jest.fn();

beforeEach(() => {
  fetch.mockClear();
});

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByText(/NoxSuite Login/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Username/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Login/i })).toBeInTheDocument();
});

test('handles login submission', async () => {
  // Mock successful login response
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ token: 'fake-jwt-token' }),
  });
  
  // Mock localStorage
  const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
  };
  Object.defineProperty(window, 'localStorage', { value: localStorageMock });
  Object.defineProperty(window, 'location', { value: { href: '' } });
  
  render(<Login />);
  
  // Fill form
  fireEvent.change(screen.getByLabelText(/Username/i), { target: { value: 'testuser' } });
  fireEvent.change(screen.getByLabelText(/Password/i), { target: { value: 'password123' } });
  
  // Submit form
  fireEvent.click(screen.getByRole('button', { name: /Login/i }));
  
  // Verify API call
  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'testuser', password: 'password123' }),
    });
  });
  
  // Verify token storage and redirect
  await waitFor(() => {
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'fake-jwt-token');
    expect(window.location.href).toBe('/dashboard');
  });
});
