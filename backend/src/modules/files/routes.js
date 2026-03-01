import { Router } from 'express';

const router = Router();

router.get('/', (_req, res) => {
  res.json({ module: 'files', message: 'Files module ready' });
});

export default router;
