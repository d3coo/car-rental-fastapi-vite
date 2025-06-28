import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
// import vitest from 'eslint-plugin-vitest'
import tseslint from 'typescript-eslint'

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  },
  // {
  //   files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
  //   plugins: {
  //     vitest,
  //   },
  //   rules: {
  //     ...vitest.configs.recommended.rules,
  //   },
  //   languageOptions: {
  //     globals: {
  //       ...vitest.environments.env.globals,
  //     },
  //   },
  // },
)