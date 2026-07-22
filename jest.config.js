module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/tests'],
  testMatch: ['**/*.test.ts'],
  moduleNameMapper: {
    '^@scm/shared$': '<rootDir>/packages/shared/src/index.ts',
    '^@scm/shared/(.*)$': '<rootDir>/packages/shared/src/$1',
    '^@scm/domain$': '<rootDir>/packages/domain/src/index.ts',
    '^@scm/domain/(.*)$': '<rootDir>/packages/domain/src/$1',
  },
  collectCoverageFrom: ['packages/*/src/**/*.ts'],
  coverageDirectory: 'coverage',
};
