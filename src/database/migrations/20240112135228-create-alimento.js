'use strict';
/** @type {import('sequelize-cli').Migration} */
module.exports = {
  async up(queryInterface, Sequelize) {
    await queryInterface.createTable('alimentos', {
      id: {
        allowNull: false,
        autoIncrement: true,
        primaryKey: true,
        type: Sequelize.INTEGER
      },
      nome: {
        type: Sequelize.STRING
      },
      carboidratos: {
        type: Sequelize.DOUBLE
      },
      proteinas: {
        type: Sequelize.DOUBLE
      },
      lipidios: {
        type: Sequelize.DOUBLE
      },
      calorias: {
        type: Sequelize.DOUBLE
      },
      vitaminas: {
        type: Sequelize.STRING
      },
      categoria_id: {
        allowNull: false,
        type: Sequelize.INTEGER,
        references: {
          model: 'categorias',
          key: 'id'
        },
      },
      createdAt: {
        allowNull: false,
        type: Sequelize.DATE
      },
      updatedAt: {
        allowNull: false,
        type: Sequelize.DATE
      }
    });
  },
  async down(queryInterface, Sequelize) {
    await queryInterface.dropTable('alimentos');
  }
};