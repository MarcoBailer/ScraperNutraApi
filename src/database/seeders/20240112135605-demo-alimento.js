'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up (queryInterface, Sequelize) {
    
    await queryInterface.bulkInsert('alimentos',  [
      {
        categoria_id: 1,
        grupo: "Cereais e derivados",
        nome: "Arroz, integral, cozido",
        carboidratos: 25.80975,
        proteinas: 2.58825,
        lipidios: 1.0003333333333333,
        calorias: 123.53489250000001,
        vitaminas: "Vitamina A: NA, Vitamina C: NA , Vitamina B1: 0.08, Vitamina B2: Tr, Vitamina B6: 0.08, Vitamina B3: Tr",
        minerais: "Cálcio: NA, Magnésio: NA, Manganês: NA, Fósforo: NA, Ferro: 0.262, Sódio: NA, Potássio: NA, Cobre: NA, Zinco: 0.6826666666666666, Selênio: NA",
        createdAt: new Date(),
        updatedAt: new Date()
      },
    ]
  , {});
    
  },

  async down (queryInterface, Sequelize) {
    await queryInterface.bulkDelete('alimentos', null, {});
  }
};
