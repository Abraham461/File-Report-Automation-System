import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';

import authRouter from './modules/auth/routes.js';
import fileRouter from './modules/files/routes.js';
import reportsRouter from './modules/reports/routes.js';
import searchRouter from './modules/search/routes.js';
import usersRouter from './modules/users/routes.js';

dotenv.config({ path: '../.env' });

const app = express();
const port = Number(process.env.APP_PORT || 4000);

app.use(cors({ origin: process.env.FRONTEND_ORIGIN || '*' }));
app.use(express.json());

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'fra-backend',
    timestamp: new Date().toISOString(),
  });
});

app.use('/api/auth', authRouter);
app.use('/api/files', fileRouter);
app.use('/api/reports', reportsRouter);
app.use('/api/search', searchRouter);
app.use('/api/users', usersRouter);

app.listen(port, () => {
  console.log(`Backend listening on http://localhost:${port}`);
});
