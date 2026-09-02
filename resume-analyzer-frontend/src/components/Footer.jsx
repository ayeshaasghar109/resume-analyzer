import "./Footer.css";

export default function Footer() {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <hr className="rule" />
      <p className="footer__text">
        © {year} Ash. All rights reserved.
      </p>
    </footer>
  );
}
