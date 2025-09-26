'use strict';

/** @type {import('sequelize-cli').Migration} */
module.exports = {
  up: (queryInterface, Sequelize) => {
    return Promise.all([
      queryInterface.addColumn('alimentos', 'grupo', {
        type: Sequelize.STRING,
        allowNull: true,
      }),
    ]);
  },
  down: (queryInterface) => {
    return Promise.all([queryInterface.removeColumn('alimentos', 'grupo')]);
  },
};
