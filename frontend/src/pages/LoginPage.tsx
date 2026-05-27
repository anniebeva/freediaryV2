import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface FormErrors {
  email?: string;
  password?: string;
}

const LoginPage: React.FunctionComponent = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    // Валидация email
    if (!email.trim()) {
      newErrors.email = 'Email обязателен';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Введите корректный email';
    }
    
    // Валидация пароля
    if (!password.trim()) {
      newErrors.password = 'Пароль обязателен';
    } else if (password.length < 6) {
      newErrors.password = 'Пароль должен содержать минимум 6 символов';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError('');
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);

    try {
      await login(email, password);
      navigate('/trainings');
    } catch (err: any) {
      if (err.message.includes('401') || err.message.includes('Необходима авторизация')) {
        setFormError('Неверный email или пароль');
      } else if (err.message.includes('400')) {
        setFormError('Неверные данные');
      } else if (err.message.includes('500')) {
        setFormError('Ошибка сервера, попробуйте позже');
      } else {
        setFormError('Ошибка при входе. Проверьте данные.');
      }
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = email.trim() && password.trim() && password.length >= 6;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-water-dark mb-6 text-center">Вход в систему</h2>
        
        {formError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {formError}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-water-dark mb-2" htmlFor="email">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (errors.email) {
                  setErrors({ ...errors, email: undefined });
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-water-medium ${
                errors.email ? 'border-red-500' : 'border-water-light'
              }`}
              required
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">{errors.email}</p>
            )}
          </div>
          
          <div className="mb-6">
            <label className="block text-water-dark mb-2" htmlFor="password">
              Пароль
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (errors.password) {
                  setErrors({ ...errors, password: undefined });
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-water-medium ${
                errors.password ? 'border-red-500' : 'border-water-light'
              }`}
              required
            />
            {errors.password && (
              <p className="text-red-500 text-sm mt-1">{errors.password}</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={loading || !isFormValid}
            className="w-full bg-water-medium text-white py-2 px-4 rounded-md hover:bg-water-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-water-dark">
            Нет аккаунта?{' '}
            <button
              onClick={() => navigate('/register')}
              className="text-water-medium hover:text-water-dark font-medium"
            >
              Зарегистрироваться
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
