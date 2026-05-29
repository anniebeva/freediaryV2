import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { telegramAPI } from '../api';

const ProfilePage: React.FunctionComponent = () => {
  const { user, logout } = useAuth();
  const [name, setName] = useState(user?.username || '');
  const [email, setEmail] = useState(user?.email || '');
  const [level, setLevel] = useState('Начинающий');
  
  // Telegram state
  const [telegramStatus, setTelegramStatus] = useState<any>(null);
  const [telegramLink, setTelegramLink] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [notificationEnabled, setNotificationEnabled] = useState(false);
  
  // Load Telegram status on component mount
  useEffect(() => {
    if (user) {
      loadTelegramStatus();
    }
  }, [user]);
  
  const loadTelegramStatus = async () => {
    try {
      const status = await telegramAPI.getStatus();
      setTelegramStatus(status);
      setNotificationEnabled(status.telegram_notifications_enabled || false);
    } catch (error) {
      console.error('Failed to load Telegram status:', error);
    }
  };
  
  const handleGenerateTelegramLink = async () => {
    setIsLoading(true);
    try {
      const result = await telegramAPI.generateLink();
      setTelegramLink(result);
      alert(`Код для привязки: ${result.code}\nСсылка: ${result.link}\n\nОткройте Telegram и напишите боту: /verify ${result.code}`);
    } catch (error) {
      console.error('Failed to generate Telegram link:', error);
      alert('Ошибка при генерации ссылки для привязки');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleUnlinkTelegram = async () => {
    if (!window.confirm('Вы уверены, что хотите отвязать Telegram?')) {
      return;
    }
    
    try {
      await telegramAPI.unlink();
      setTelegramStatus(null);
      setTelegramLink(null);
      setNotificationEnabled(false);
      alert('Telegram успешно отвязан');
    } catch (error) {
      console.error('Failed to unlink Telegram:', error);
      alert('Ошибка при отвязке Telegram');
    }
  };
  
  const handleSendTestNotification = async () => {
    try {
      await telegramAPI.sendTestNotification();
      alert('Тестовое уведомление отправлено');
    } catch (error) {
      console.error('Failed to send test notification:', error);
      alert('Ошибка при отправке тестового уведомления');
    }
  };
  
  const handleToggleNotifications = async (enabled: boolean) => {
    try {
      await telegramAPI.updateSettings(enabled);
      setNotificationEnabled(enabled);
      alert(`Уведомления ${enabled ? 'включены' : 'отключены'}`);
    } catch (error) {
      console.error('Failed to update notification settings:', error);
      alert('Ошибка при обновлении настроек уведомлений');
    }
  };

  const handleSaveProfile = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Реализовать сохранение профиля
    alert('Профиль обновлен');
  };

  if (!user) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-white shadow-md rounded-lg p-6 text-center">
          <h2 className="text-2xl font-bold text-water-dark mb-4">Вы не авторизованы</h2>
          <p className="text-water-dark mb-6">Пожалуйста, войдите в систему, чтобы просмотреть профиль</p>
          <a 
            href="/login" 
            className="bg-water-medium text-white py-2 px-6 rounded hover:bg-water-dark transition inline-block"
          >
            Войти
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-water-dark mb-6">Профиль</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-bold text-water-dark mb-4">Информация о пользователе</h2>
          <div className="mb-4">
            <p className="text-water-dark font-bold">Имя пользователя:</p>
            <p className="text-water-medium">{user.username}</p>
          </div>
          <div className="mb-4">
            <p className="text-water-dark font-bold">Email:</p>
            <p className="text-water-medium">{user.email}</p>
          </div>
          <div className="mb-6">
            <p className="text-water-dark font-bold">ID пользователя:</p>
            <p className="text-water-medium text-sm">{user.id}</p>
          </div>
          <button
            onClick={logout}
            className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition"
          >
            Выйти из профиля
          </button>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-bold text-water-dark mb-4">Настройки профиля</h2>
          <form onSubmit={handleSaveProfile}>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Отображаемое имя</label>
              <input 
                type="text" 
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-3 py-2 border border-water-light rounded focus:outline-none focus:ring-2 focus:ring-water-medium"
              />
            </div>

            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Email для уведомлений</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-water-light rounded focus:outline-none focus:ring-2 focus:ring-water-medium"
              />
            </div>

            <div className="mb-6">
              <label className="block text-water-dark font-bold mb-2">Уровень подготовки</label>
              <select 
                value={level}
                onChange={(e) => setLevel(e.target.value)}
                className="w-full px-3 py-2 border border-water-light rounded focus:outline-none focus:ring-2 focus:ring-water-medium"
              >
                <option value="Начинающий">Начинающий</option>
                <option value="Любитель">Любитель</option>
                <option value="Профессионал">Профессионал</option>
              </select>
            </div>

            <button 
              type="submit"
              className="w-full bg-water-medium text-white py-3 rounded hover:bg-water-dark transition"
            >
              Сохранить настройки
            </button>
          </form>
        </div>

        <div className="bg-white shadow-md rounded-lg p-6">
          <h2 className="text-xl font-bold text-water-dark mb-4">Telegram уведомления</h2>
          
          {telegramStatus?.telegram_linked ? (
            <>
              <div className="mb-4">
                <p className="text-water-dark font-bold">Статус:</p>
                <p className="text-green-600 font-bold">✅ Привязан</p>
              </div>
              
              <div className="mb-4">
                <p className="text-water-dark font-bold">Telegram ID:</p>
                <p className="text-water-medium text-sm">{telegramStatus.telegram_id}</p>
              </div>
              
              <div className="mb-6">
                <label className="flex items-center space-x-2">
                  <input 
                    type="checkbox" 
                    checked={notificationEnabled}
                    onChange={(e) => handleToggleNotifications(e.target.checked)}
                    className="h-5 w-5 text-water-medium rounded focus:ring-water-medium"
                  />
                  <span className="text-water-dark font-bold">Включить уведомления</span>
                </label>
                <p className="text-water-light text-sm mt-1">
                  Получать уведомления о входе в систему и тренировках
                </p>
              </div>
              
              <div className="space-y-3">
                <button
                  onClick={handleSendTestNotification}
                  disabled={!notificationEnabled}
                  className={`w-full py-2 px-4 rounded transition ${
                    notificationEnabled 
                      ? 'bg-blue-500 text-white hover:bg-blue-600' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Отправить тестовое уведомление
                </button>
                
                <button
                  onClick={handleUnlinkTelegram}
                  className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 transition"
                >
                  Отвязать Telegram
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-4">
                <p className="text-water-dark font-bold">Статус:</p>
                <p className="text-red-600 font-bold">❌ Не привязан</p>
              </div>
              
              <div className="mb-6">
                <p className="text-water-dark mb-3">
                  Привяжите Telegram, чтобы получать уведомления о:
                </p>
                <ul className="list-disc pl-5 text-water-medium space-y-1">
                  <li>Входе в систему</li>
                  <li>Создании тренировок</li>
                  <li>Удалении тренировок</li>
                </ul>
              </div>
              
              <button
                onClick={handleGenerateTelegramLink}
                disabled={isLoading}
                className="w-full bg-green-500 text-white py-3 rounded hover:bg-green-600 transition disabled:bg-green-300"
              >
                {isLoading ? 'Генерация ссылки...' : 'Привязать Telegram'}
              </button>
              
              {telegramLink && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <p className="text-blue-800 font-bold mb-1">Код для привязки:</p>
                  <p className="text-blue-900 font-mono text-lg mb-2">{telegramLink.code}</p>
                  <p className="text-blue-800 text-sm mb-2">
                    Откройте Telegram и напишите боту: <strong>/verify {telegramLink.code}</strong>
                  </p>
                  <a 
                    href={telegramLink.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 text-sm underline"
                  >
                    Открыть Telegram бота
                  </a>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
