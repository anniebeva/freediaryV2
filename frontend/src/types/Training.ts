// Типы данных для тренировок
export enum TrainingType {
  Pool = 'Бассейн',
  Depth = 'Глубина',
  Gym = 'Зал',
  Other = 'Другое'
}

export interface Exercise {
  id: string;
  name: string;
  notes: string;
}

export interface Training {
  id: string;
  type: TrainingType;
  date: Date;
  difficulty: number; // 1-5
  notes?: string;
  
  // Специфические поля для разных типов тренировок
  poolTraining?: {
    poolSize?: number;
  };
  
  depthTraining?: {
    wetsuit?: number; // толщина костюма в мм
    temperature?: number;
    weights?: number;
    location?: string;
    maxDepth?: number;
  };
  
  gymTraining?: {
    avgHeartRate?: number;
    maxHeartRate?: number;
    calories?: number;
  };
  
  exercises: Exercise
}
