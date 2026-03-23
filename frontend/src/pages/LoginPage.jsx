import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { MolLoadingPage } from '../atomic/MolLoadingPage';
import { MolLabeledInput } from '../atomic/MolLabeledInput';
import { ObjAppLayout as BaseLayout } from '../atomic/ObjAppLayout';
import { Button, LinkButton } from '../atomic/AtmButton/index.js';
import { AtmText } from '../atomic/AtmText/index.js';
import { LoginApi } from '../services/api.js';

function LoginPage({ isLoading, setIsLoading }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (email, password) => {
    setIsLoading(true);
    try {
      const response = await LoginApi.authenticateUser(email, password);
      localStorage.setItem('token', response.data.access_token);
      navigate('/staff');
    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 401) {
        alert(err.response.data.detail || 'Invalid email or password');
      }
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleLogin(email, password);
  };

  if (isLoading) return (
    <BaseLayout currentPage={0} showSidebar={false}>
      <MolLoadingPage />
    </BaseLayout>
  );

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="bg-slate-800 p-8 rounded-xl shadow-2xl w-full max-w-md border border-slate-600">
        <AtmText as="h3" size="2xl" weight="semibold" color="dimmer" className="mb-6 text-center block">Login</AtmText>
        <form onSubmit={handleSubmit} className="space-y-4">
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
            Enter
          </Button>
        </form>
        <div className="mt-5 text-center">
          <AtmText as="p" size="sm" color="muted">
            Don't have an account?{' '}
            <LinkButton onClick={() => navigate('/register')}>
              Register
            </LinkButton>
          </AtmText>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
