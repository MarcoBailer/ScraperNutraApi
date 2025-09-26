const { Router } = require('express'); 
const AlimentoController = require('../controller/AlimentoController.js');

const alimentoController = new AlimentoController();

const router = Router();

router.get('/alimentos', (req, res) => alimentoController.getAll(req, res));
router.get('/alimentos/:id', (req, res) => alimentoController.getById(req, res));
router.get('/alimentos/nome/:nome', (req, res) => alimentoController.getByName(req, res));
router.get('/alimentos/grupo/:grupo', (req, res) => alimentoController.getAllFromCategory(req, res));
router.post('/alimentos', (req, res) => alimentoController.create(req, res));
router.post('/alimentos/many', (req, res) => alimentoController.createMany(req, res));
router.put('/alimentos/:id', (req, res) => alimentoController.update(req, res));
router.delete('/alimentos/:id', (req, res) => alimentoController.delete(req, res));

module.exports = router;