const Controller = require('./Controller.js');
const AlimentoService = require('../service/AlimentoService.js');

const alimentoService = new AlimentoService();

class AlimentoController extends Controller{
    constructor(){
        super(alimentoService);
    }
}

module.exports = AlimentoController;