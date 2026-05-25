import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { TrainingType } from '../types/Training';
import { trainingAPI, exerciseAPI } from '../api';
import { v4 as uuidv4 } from 'uuid';

interface Exercise {
  id: string;
  name: string;
  notes: string;
}

const mapTrainingTypeToAPI = (type: TrainingType): string => {
  switch (type) {
    case TrainingType.Pool:
      return 'Pool';
    case TrainingType.Depth:
      return 'Depth';
    case TrainingType.Gym:
      return 'Gym';
    default:
      return 'Other';
  }
};

const EditTrainingPage: React.FunctionComponent = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  
  const [trainingType, setTrainingType] = useState<TrainingType>(TrainingType.Pool);
  const [difficulty, setDifficulty] = useState<number>(3);
  const [notes, setNotes] = useState<string>('');
  const [date, setDate] = useState<string>('');
  const [exercises, setExercises] = useState<Exercise[]>([]);

  // Специфические состояния для разных типов тренировок
  const [poolTraining, setPoolTraining] = useState({ poolSize: 0 });
  const [depthTraining, setDepthTraining] = useState({
    wetsuit: 0,
    temperature: 0,
    location: '',
  });
  const [gymTraining, setGymTraining] = useState({
    avgHeartRate: 0,
    calories: 0,
  });

  useEffect(() => {
    const fetchTraining = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await trainingAPI.getById(id);
        
        // Определяем тип тренировки из строки, которую вернул бэкенд
        const typeString = data.type;
        let mappedType = TrainingType.Pool;
        if (typeString === 'Depth') mappedType = TrainingType.Depth;
        else if (typeString === 'Gym') mappedType = TrainingType.Gym;
        else mappedType = TrainingType.Pool;
        
        setTrainingType(mappedType);
        setDifficulty(data.difficulty);
        setNotes(data.notes || '');
        setDate(data.date);
        
        // Загружаем специфические данные с проверкой на null/undefined
        if (data.poolTraining && Object.keys(data.poolTraining).length > 0) {
          setPoolTraining(data.poolTraining);
        } else {
          setPoolTraining({ poolSize: 0 });
        }
        
        if (data.depthTraining && Object.keys(data.depthTraining).length > 0) {
          setDepthTraining(data.depthTraining);
        } else {
          setDepthTraining({
            wetsuit: 0,
            temperature: 0,
            location: '',
          });
        }
        
        if (data.gymTraining && Object.keys(data.gymTraining).length > 0) {
          setGymTraining(data.gymTraining);
        } else {
          setGymTraining({
            avgHeartRate: 0,
            calories: 0,
          });
        }
        
        // Загружаем упражнения из бэкенда
        if (data.exercises && Array.isArray(data.exercises)) {
          setExercises(data.exercises.map((ex: any) => ({
            id: ex.id.toString(),
            name: ex.name,
            notes: ex.notes || '',
          })));
        }
      } catch (err: any) {
        console.error('Error fetching training:', err);
        setSubmitError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTraining();
  }, [id]);

  const handleAddExercise = () => {
    const newExercise: Exercise = {
      id: uuidv4(),
      name: '',
      notes: '',
    };
    setExercises([...exercises, newExercise]);
  };

  const handleRemoveExercise = (exerciseId: string) => {
    setExercises(exercises.filter(ex => ex.id !== exerciseId));
  };

  const handleExerciseChange = (exerciseId: string, field: keyof Exercise, value: string) => {
    setExercises(exercises.map(ex => 
      ex.id === exerciseId ? { ...ex, [field]: value } : ex
    ));
  };

  const validateForm = (): boolean => {
    // Проверяем, что у всех упражнений (если они есть) есть название
    const emptyName = exercises.some(ex => !ex.name.trim());
    if (emptyName) {
      setSubmitError('У всех упражнений должно быть название');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    setSubmitError(null);
    
    try {
      const trainingData: any = {
        type: mapTrainingTypeToAPI(trainingType),
        date: date,
        difficulty: difficulty,
      };
      
      if (notes.trim()) {
        trainingData.notes = notes;
      }
      
      if (trainingType === TrainingType.Pool) {
        trainingData.poolTraining = poolTraining;
      } else if (trainingType === TrainingType.Depth) {
        trainingData.depthTraining = depthTraining;
      } else if (trainingType === TrainingType.Gym) {
        trainingData.gymTraining = gymTraining;
      }

      // 1. Обновляем тренировку
      await trainingAPI.update(id!, trainingData);
      
      // 2. Получаем текущие упражнения с бэка
      const currentExercises = await exerciseAPI.getByTraining(id!);
      
      // Создаём Map для быстрого поиска
      const currentExercisesMap = new Map(currentExercises.map((ex: any) => [ex.id.toString(), ex]));
      const newExercisesMap = new Map(exercises.map(ex => [ex.id, ex]));
      
      // Удаляем упражнения, которых нет в новой версии
      for (const exId of Array.from(currentExercisesMap.keys())) {
        if (!newExercisesMap.has(exId)) {
          await exerciseAPI.delete(exId);
        }
      }
      
      // Обновляем или создаём упражнения
      for (const exercise of exercises) {
        const exerciseData = {
          name: exercise.name,
          notes: exercise.notes || undefined,
          training_id: parseInt(id!),
        };
        
        if (currentExercisesMap.has(exercise.id) && !exercise.id.includes('uuid')) {
          // Обновляем существующее упражнение (если id не начинается с uuid - значит из бэка)
          await exerciseAPI.update(exercise.id, exerciseData);
        } else if (exercise.name.trim()) {
          // Создаём новое упражнение (если есть название)
          await exerciseAPI.create(exerciseData);
        }
      }
      
      navigate(`/training/${id}`);
    } catch (err: any) {
      console.error('Error updating training:', err);
      setSubmitError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center text-gray-600">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold text-water-dark mb-6">Изменить тренировку</h1>
      
      <form onSubmit={handleSubmit} className="bg-white shadow-md rounded-lg p-6">
        <div className="mb-4">
          <label className="block text-water-dark font-bold mb-2">Тип тренировки</label>
          <select 
            value={trainingType} 
            onChange={(e) => setTrainingType(e.target.value as TrainingType)}
            className="w-full px-3 py-2 border rounded"
          >
            {Object.values(TrainingType).map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>

        <div className="mb-4">
          <label className="block text-water-dark font-bold mb-2">Дата тренировки</label>
          <input 
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full px-3 py-2 border rounded"
          />
        </div>

        <div className="mb-4">
          <label className="block text-water-dark font-bold mb-2">
            Сложность тренировки: {difficulty}
          </label>
          <input
            type="range"
            min="1"
            max="5"
            step="1"
            value={difficulty}
            onChange={(e) => setDifficulty(Number(e.target.value))}
            className="w-full"
          />
        </div>

        <div className="mb-4">
          <label className="block text-water-dark font-bold mb-2">Заметки</label>
          <textarea 
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full px-3 py-2 border rounded"
            placeholder="Дополнительные заметки о тренировке"
          />
        </div>

        {/* Специфические поля для разных типов тренировок */}
        {trainingType === TrainingType.Pool && (
          <div className="mb-4">
            <label className="block text-water-dark font-bold mb-2">Размер бассейна (м)</label>
            <input 
              type="number" 
              value={poolTraining.poolSize}
              onChange={(e) => setPoolTraining({ poolSize: Number(e.target.value) })}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
        )}

        {trainingType === TrainingType.Depth && (
          <>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Толщина костюма (мм)</label>
              <input 
                type="number" 
                value={depthTraining.wetsuit}
                onChange={(e) => setDepthTraining({...depthTraining, wetsuit: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Температура воды (°C)</label>
              <input 
                type="number" 
                value={depthTraining.temperature}
                onChange={(e) => setDepthTraining({...depthTraining, temperature: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Локация</label>
              <input 
                type="text" 
                value={depthTraining.location}
                onChange={(e) => setDepthTraining({...depthTraining, location: e.target.value})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
          </>
        )}

        {trainingType === TrainingType.Gym && (
          <>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Средний пульс</label>
              <input 
                type="number" 
                value={gymTraining.avgHeartRate}
                onChange={(e) => setGymTraining({...gymTraining, avgHeartRate: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div className="mb-4">
              <label className="block text-water-dark font-bold mb-2">Калории</label>
              <input 
                type="number" 
                value={gymTraining.calories}
                onChange={(e) => setGymTraining({...gymTraining, calories: Number(e.target.value)})}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
          </>
        )}

        {/* Упражнения — единый блок */}
        <div className="border-t border-water-light pt-4 mb-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-semibold text-water-medium">Упражнения</h2>
            <button 
              type="button"
              onClick={handleAddExercise}
              className="bg-water-medium text-white px-3 py-1 rounded hover:bg-water-dark transition"
            >
              + Добавить упражнение
            </button>
          </div>

          {exercises.length === 0 && (
            <p className="text-gray-500 text-center py-4">Нет упражнений</p>
          )}

          {exercises.map((exercise) => (
            <div 
              key={exercise.id} 
              className="bg-water-light/50 rounded p-3 mb-3 flex justify-between items-start gap-2"
            >
              <div className="flex-1">
                <input 
                  type="text"
                  value={exercise.name}
                  onChange={(e) => handleExerciseChange(exercise.id, 'name', e.target.value)}
                  className="font-semibold mb-2 w-full px-2 py-1 rounded border"
                  placeholder="Название упражнения"
                />
                <textarea 
                  value={exercise.notes}
                  onChange={(e) => handleExerciseChange(exercise.id, 'notes', e.target.value)}
                  className="w-full px-2 py-1 rounded border"
                  placeholder="Заметки об упражнении"
                  rows={2}
                />
              </div>
              <button 
                type="button"
                onClick={() => handleRemoveExercise(exercise.id)}
                className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 transition"
              >
                Удалить
              </button>
            </div>
          ))}
        </div>

        {submitError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <p>{submitError}</p>
          </div>
        )}
        
        <button 
          type="submit"
          disabled={saving}
          className={`w-full py-3 rounded transition ${
            saving 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-water-medium text-white hover:bg-water-dark'
          }`}
        >
          {saving ? 'Сохранение...' : 'Сохранить изменения'}
        </button>
      </form>
    </div>
  );
};

export default EditTrainingPage;