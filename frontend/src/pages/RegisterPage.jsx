import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { MolLabeledInput } from '../atomic/MolLabeledInput';
import { Button, LinkButton } from '../atomic/AtmButton/index.js';
import { AtmText } from '../atomic/AtmText/index.js';
import { RegisterApi } from '../services/api.js';

function RegisterPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [confEmail, setConfEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRegister = async (email, confEmail, password, setError) => {
    try {
      const responseRegister = await RegisterApi.registerUser(email, password);
      if (responseRegister.data) {
        alert('User registered successfully');
        navigate('/login');
      }
    } catch (error) {
      if (error.response?.data?.detail === 'Email already registered') {
        setError('Email already registered');
      } else {
        setError('Error registering user. Please try again.');
      }
      console.error('Registration error:', error.response?.data);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password || !confEmail) {
      setError('Fill in all fields');
      return;
    }
    if (email !== confEmail) {
      setError('The emails are not the same');
      return;
    }
    handleRegister(email, confEmail, password, setError);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-slate-600">
        <AtmText as="h3" size="2xl" weight="semibold" color="dimmer" className="mb-6 text-center block">Register</AtmText>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-900/50 border border-red-700 rounded-lg">
              <AtmText size="sm" color="red">{error}</AtmText>
            </div>
          )}
          <MolLabeledInput
            label="Email"
            id="email"
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            variant='auth'
          />
          <MolLabeledInput
            label="Confirm Email"
            id="confirm-email"
            type="email"
            placeholder="Confirm your email"
            value={confEmail}
            onChange={(e) => setConfEmail(e.target.value)}
            required
            variant='auth'
          />
          <MolLabeledInput
            label="Password"
            id="password"
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mb-2"
            variant='auth'
          />
          <Button type="submit" fullWidth variant='primary' size='lg'>
            Register
          </Button>
        </form>
        <div className="mt-5 text-center">
          <AtmText as="p" size="sm" color="muted">
            Already have an account?{' '}
            <LinkButton onClick={() => navigate('/login')}>
              Login
            </LinkButton>
          </AtmText>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
