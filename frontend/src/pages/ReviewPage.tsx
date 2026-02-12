export function ReviewPage() {
  const linksRaw = sessionStorage.getItem('review_links')
  const links = linksRaw ? (JSON.parse(linksRaw) as { '2gis': string; yandex: string }) : null

  return (
    <div className="container centered">
      <h1>Спасибо за высокую оценку!</h1>
      <p>Будем рады отзыву на внешних площадках:</p>
      <div className="card-list">
        <a href={links?.['2gis'] ?? '#'} target="_blank" rel="noreferrer" className="big-button">
          Оставить отзыв в 2ГИС
        </a>
        <a href={links?.yandex ?? '#'} target="_blank" rel="noreferrer" className="big-button">
          Оставить отзыв в Яндекс
        </a>
      </div>
    </div>
  )
}
