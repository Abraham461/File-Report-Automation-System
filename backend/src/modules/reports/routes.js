import { Router } from 'express';

const router = Router();

router.get('/', (_req, res) => {
  res.json({ module: 'reports', message: 'Reports module ready' });
});

export default router;
