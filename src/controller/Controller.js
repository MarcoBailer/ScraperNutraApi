class Controller {
    constructor(entityService){
        this.entityService = entityService;
    }
    async getAll(req,res){
        try{
            const allEntities = await this.entityService.getAllService();
            return res.status(200).json(allEntities);
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async getById(req,res){
        const { id } = req.params;
        try{
            const entity = await this.entityService.getByIdService(id);
            return res.status(200).json(entity);
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async getByName(req,res){
        const { nome } = req.params;
        try{
            const entity = await this.entityService.getByNomeService(nome);
            return res.status(200).json(entity);
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async getAllFromCategory(req,res){
        const { grupo } = req.params;
        try{
            const entity = await this.entityService.getAllFromCategoryService(grupo);
            return res.status(200).json({Alimentos: entity});
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async create(req,res){
        const entity = req.body;
        try{
            const createdEntity = await this.entityService.createService(entity);
            return res.status(201).json(createdEntity);
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    //recebe um array de entidades
    async createMany(req,res){
        const entities = req.body;
        try{
            const createdEntities = await this.entityService.createManyService(entities);
            return res.status(201).json(createdEntities);
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async update(req,res){
        const { id } = req.params;
        const entity = req.body;
        try{
            const updatedEntity = await this.entityService.updateService(id, entity);
            return res.status(200).json(updatedEntity);
            if(!updatedEntity){
                return res.status(404).json({message: 'Not found'});
            }
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
    async delete(req,res){
        const { id } = req.params;
        try{
            await this.entityService.deleteService(id);
            return res.status(200).json({message: 'Deleted'});
        }catch(error){
            return res.status(500).json(error.message);
        }
    }
}

module.exports = Controller;