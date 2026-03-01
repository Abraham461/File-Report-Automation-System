import { Router } from 'express';

const router = Router();

router.get('/', (_req, res) => {
  res.json({ module: 'users', message: 'Users module ready' });
});

export default router;
