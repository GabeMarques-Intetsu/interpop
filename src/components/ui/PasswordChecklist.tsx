import { PASSWORD_RULES } from '@/utils/passwordRules';
import './PasswordChecklist.css';

interface PasswordChecklistProps {
  value: string;
  /** Esconde o checklist enquanto o campo está vazio (evita "tudo vermelho" no load). */
  hideWhenEmpty?: boolean;
}

/**
 * Checklist de força de senha ao vivo. Mostra as 5 regras com ✓/✗ conforme o
 * usuário digita. Usado em Register, ResetPassword e troca de senha no Perfil —
 * mesma fonte de regras do backend (passwordRules.ts ↔ PasswordComplexityValidator).
 */
export function PasswordChecklist({
  value,
  hideWhenEmpty = true,
}: PasswordChecklistProps) {
  if (hideWhenEmpty && value.length === 0) return null;

  return (
    <ul className="pw-checklist" aria-label="Requisitos da senha">
      {PASSWORD_RULES.map((rule) => {
        const ok = rule.test(value);
        return (
          <li
            key={rule.id}
            className={`pw-checklist__item ${ok ? 'pw-checklist__item--ok' : 'pw-checklist__item--fail'}`}
            aria-label={`${rule.label}: ${ok ? 'cumprido' : 'pendente'}`}
          >
            <span className="pw-checklist__icon" aria-hidden="true">
              {ok ? '✓' : '✗'}
            </span>
            <span className="pw-checklist__label" aria-hidden="true">
              {rule.label}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
