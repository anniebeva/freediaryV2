import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface FormErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

const RegisterPage: React.FunctionComponent = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<FormErrors>({});
  const [formError, setFormError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    
    // Валидация имени пользователя
    if (!username.trim()) {
      newErrors.username = 'Имя пользователя обязательно';
    } else if (username.length < 3) {
      newErrors.username = 'Имя пользователя должно быть не менее 3 символов';
    } else if (username.length > 50) {
      newErrors.username = 'Имя пользователя должно быть не более 50 символов';
    }
    
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
    
    // Валидация подтверждения пароля
    if (!confirmPassword.trim()) {
      newErrors.confirmPassword = 'Подтверждение пароля обязательно';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
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
      await register(username, email, password);
      navigate('/trainings');
    } catch (err: any) {
      if (err.message.includes('400')) {
        if (err.message.includes('пользователь') || err.message.includes('email')) {
          setFormError('Пользователь с таким email уже существует');
        } else {
          setFormError('Неверные данные для регистрации');
        }
      } else if (err.message.includes('500')) {
        setFormError('Ошибка сервера, попробуйте позже');
      } else {
        setFormError('Ошибка при регистрации. Попробуйте позже.');
      }
      console.error('Register error:', err);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid = username.trim() && username.length >= 3 && username.length <= 50 &&
                     email.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) &&
                     password.trim() && password.length >= 6 &&
                     confirmPassword.trim() && password === confirmPassword;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-water-dark mb-6 text-center">Регистрация</h2>
        
        {formError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {formError}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-water-dark mb-2" htmlFor="username">
              Имя пользователя
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                if (errors.username) {
                  setErrors({ ...errors, username: undefined });
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-water-medium ${
                errors.username ? 'border-red-500' : 'border-water-light'
              }`}
              required
            />
            {errors.username && (
              <p className="text-red-500 text-sm mt-1">{errors.username}</p>
            )}
          </div>
          
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
          
          <div className="mb-4">
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
                if (errors.confirmPassword) {
                  setErrors({ ...errors, confirmPassword: undefined });
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
          
          <div className="mb-6">
            <label className="block text-water-dark mb-2" htmlFor="confirmPassword">
              Подтвердите пароль
            </label>
            <input
              type="password"
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (errors.confirmPassword) {
                  setErrors({ ...errors, confirmPassword: undefined });
                }
              }}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-water-medium ${
                errors.confirmPassword ? 'border-red-500' : 'border-water-light'
              }`}
              required
            />
            {errors.confirmPassword && (
              <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={loading || !isFormValid}
            className="w-full bg-water-medium text-white py-2 px-4 rounded-md hover:bg-water-dark transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>
        
        <div className="mt-6 text-center">
          <p className="text-water-dark">
            Уже есть аккаунт?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-water-medium hover:text-water-dark font-medium"
            >
              Войти
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
