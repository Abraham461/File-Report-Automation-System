import { Router } from 'express';

const router = Router();

router.get('/', (_req, res) => {
  res.json({ module: 'auth', message: 'Auth module ready' });
});

export default router;
