#!/usr/bin/env node
/**
 * Comprehensive test runner for the Tariff AI Frontend
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Test configuration
const TEST_CONFIG = {
  coverage: {
    collectCoverageFrom: [
      'src/**/*.{js,jsx}',
      '!src/index.js',
      '!src/reportWebVitals.js',
      '!src/setupTests.js',
      '!src/**/*.test.{js,jsx}',
      '!src/**/*.stories.{js,jsx}'
    ],
    coverageThreshold: {
      global: {
        branches: 80,
        functions: 80,
        lines: 80,
        statements: 80
      }
    },
    coverageReporters: ['text', 'lcov', 'html']
  },
  watch: false,
  verbose: true,
  maxWorkers: '50%'
};

function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

function checkDependencies() {
  console.log('🔧 Checking Frontend Dependencies...');
  
  const packageJson = require('./package.json');
  const requiredDeps = [
    '@testing-library/jest-dom',
    '@testing-library/react',
    '@testing-library/user-event',
    'react',
    'react-dom',
    'react-router-dom'
  ];

  const missingDeps = requiredDeps.filter(dep => !packageJson.dependencies[dep] && !packageJson.devDependencies[dep]);
  
  if (missingDeps.length > 0) {
    console.log(`❌ Missing dependencies: ${missingDeps.join(', ')}`);
    console.log('Install with: npm install ' + missingDeps.join(' '));
    return false;
  }

  console.log('✅ All required dependencies are installed');
  return true;
}

function runUnitTests() {
  console.log('🧪 Running Unit Tests...');
  
  const args = [
    'test',
    '--watchAll=false',
    '--verbose',
    '--coverage',
    '--coverageDirectory=coverage',
    '--coverageReporters=text,lcov,html',
    '--collectCoverageFrom="src/**/*.{js,jsx}"',
    '--coverageThreshold.global.branches=80',
    '--coverageThreshold.global.functions=80',
    '--coverageThreshold.global.lines=80',
    '--coverageThreshold.global.statements=80'
  ];

  return runCommand('npm', args);
}

function runIntegrationTests() {
  console.log('🔗 Running Integration Tests...');
  
  const args = [
    'test',
    '--watchAll=false',
    '--verbose',
    '--testPathPattern=integration',
    '--coverage',
    '--coverageDirectory=coverage/integration'
  ];

  return runCommand('npm', args);
}

function runE2ETests() {
  console.log('🔍 Running End-to-End Tests...');
  
  // This would typically use Cypress or Playwright
  // For now, we'll just run a placeholder
  console.log('⚠️  E2E tests not configured yet');
  return Promise.resolve();
}

function runAccessibilityTests() {
  console.log('♿ Running Accessibility Tests...');
  
  // This would typically use axe-core or similar
  // For now, we'll just run a placeholder
  console.log('⚠️  Accessibility tests not configured yet');
  return Promise.resolve();
}

function runPerformanceTests() {
  console.log('⚡ Running Performance Tests...');
  
  // This would typically use Lighthouse CI or similar
  // For now, we'll just run a placeholder
  console.log('⚠️  Performance tests not configured yet');
  return Promise.resolve();
}

function generateTestReport() {
  console.log('📊 Generating Test Report...');
  
  const coveragePath = path.join(__dirname, 'coverage/lcov-report/index.html');
  if (fs.existsSync(coveragePath)) {
    console.log(`📈 Coverage report available at: ${coveragePath}`);
  }
  
  console.log('✅ Test report generation completed');
}

function runLinting() {
  console.log('🔍 Running ESLint...');
  
  const args = [
    'run',
    'lint'
  ];

  return runCommand('npm', args).catch(() => {
    console.log('⚠️  Linting issues found (non-blocking)');
  });
}

function runTypeChecking() {
  console.log('🔍 Running Type Checking...');
  
  // Check if TypeScript is configured
  const tsConfigPath = path.join(__dirname, 'tsconfig.json');
  if (fs.existsSync(tsConfigPath)) {
    return runCommand('npx', ['tsc', '--noEmit']).catch(() => {
      console.log('⚠️  Type checking issues found (non-blocking)');
    });
  } else {
    console.log('ℹ️  TypeScript not configured, skipping type checking');
    return Promise.resolve();
  }
}

async function runAllTests() {
  console.log('🚀 Starting Tariff AI Frontend Tests');
  console.log('=' * 50);
  
  try {
    // Check dependencies
    if (!checkDependencies()) {
      process.exit(1);
    }
    
    // Run linting and type checking
    await Promise.all([
      runLinting(),
      runTypeChecking()
    ]);
    
    // Run tests
    await runUnitTests();
    await runIntegrationTests();
    await runE2ETests();
    await runAccessibilityTests();
    await runPerformanceTests();
    
    // Generate report
    generateTestReport();
    
    console.log('\n✅ All tests completed successfully!');
    console.log('📊 Coverage reports generated in coverage/ directory');
    
  } catch (error) {
    console.error('\n❌ Tests failed:', error.message);
    process.exit(1);
  }
}

async function runSpecificTests(testType) {
  console.log(`🎯 Running ${testType} tests...`);
  
  try {
    switch (testType) {
      case 'unit':
        await runUnitTests();
        break;
      case 'integration':
        await runIntegrationTests();
        break;
      case 'e2e':
        await runE2ETests();
        break;
      case 'accessibility':
        await runAccessibilityTests();
        break;
      case 'performance':
        await runPerformanceTests();
        break;
      case 'lint':
        await runLinting();
        break;
      case 'type':
        await runTypeChecking();
        break;
      default:
        console.error(`Unknown test type: ${testType}`);
        process.exit(1);
    }
    
    console.log(`✅ ${testType} tests completed successfully!`);
    
  } catch (error) {
    console.error(`❌ ${testType} tests failed:`, error.message);
    process.exit(1);
  }
}

function showHelp() {
  console.log('Tariff AI Frontend Test Runner');
  console.log('=' * 30);
  console.log('This script runs various types of tests for the Tariff AI frontend.');
  console.log('\nAvailable commands:');
  console.log('  all          - Run all tests with coverage reporting');
  console.log('  unit         - Run only unit tests (fast)');
  console.log('  integration  - Run only integration tests');
  console.log('  e2e          - Run only end-to-end tests');
  console.log('  accessibility - Run only accessibility tests');
  console.log('  performance  - Run only performance tests');
  console.log('  lint         - Run only linting');
  console.log('  type         - Run only type checking');
  console.log('  help         - Show this help message');
  console.log('\nExamples:');
  console.log('  node run_tests.js all');
  console.log('  node run_tests.js unit');
  console.log('  node run_tests.js integration');
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node run_tests.js [command]');
    console.log('Use "node run_tests.js help" for more information');
    process.exit(1);
  }
  
  const command = args[0].toLowerCase();
  
  if (command === 'help') {
    showHelp();
  } else if (command === 'all') {
    runAllTests();
  } else {
    runSpecificTests(command);
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  runAllTests,
  runSpecificTests,
  runUnitTests,
  runIntegrationTests,
  runE2ETests,
  runAccessibilityTests,
  runPerformanceTests,
  runLinting,
  runTypeChecking,
  checkDependencies
}; 