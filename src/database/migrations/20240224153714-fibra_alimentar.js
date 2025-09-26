'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  up: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.addColumn('alimentos', 'fibra_alimentar', {
        type: Sequelize.DOUBLE,
        allowNull: true,
      }),
    ]);
  },
  down: (queryInterface) => {
    return Promise.all([queryInterface.removeColumn('alimentos', 'fibra_alimentar')]);
  },
};
