import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Home } from '../pages/Home';
import { News } from '../pages/News';
import { Newsletter } from '../pages/Newsletter';
import { About } from '../pages/About';
import { Termos } from '../pages/Legal/Termos';
import { Privacidade } from '../pages/Legal/Privacidade';
import { Article } from '../pages/Article';
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { ForgotPassword } from '../pages/ForgotPassword';
import { ResetPassword } from '../pages/ResetPassword';
import { Admin } from '../pages/Admin';
import { CreatePost } from '../pages/CreatePost';
import { AdminRoute } from './AdminRoute';
import { ScrollToHashOrTop } from './ScrollToHashOrTop';

export function AppRouter() {
  return (
    <BrowserRouter>
      <ScrollToHashOrTop />
      <Routes>
        <Route path="/"                         element={<Home />} />
        <Route path="/noticias"                 element={<News />} />
        <Route path="/newsletter"               element={<Newsletter />} />
        <Route path="/sobre"                    element={<About />} />
        <Route path="/termos"                   element={<Termos />} />
        <Route path="/privacidade"              element={<Privacidade />} />
        <Route path="/noticia/:slug"            element={<Article />} />
        <Route path="/login"                    element={<Login />} />
        <Route path="/cadastro"                 element={<Register />} />
        <Route path="/recuperar-senha"          element={<ForgotPassword />} />
        <Route path="/redefinir-senha/:token"   element={<ResetPassword />} />
        <Route
          path="/admin"
          element={<AdminRoute><Admin /></AdminRoute>}
        />
        <Route
          path="/criar-publicacao"
          element={<AdminRoute><CreatePost /></AdminRoute>}
        />
      </Routes>
    </BrowserRouter>
  );
}
