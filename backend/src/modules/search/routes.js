import { Router } from 'express';

const router = Router();

router.get('/', (_req, res) => {
  res.json({ module: 'search', message: 'Search module ready' });
});

export default router;
